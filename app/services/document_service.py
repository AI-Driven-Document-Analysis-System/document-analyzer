import os
import hashlib
import mimetypes
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from typing import Tuple, Optional, Dict, Any, List
from uuid import uuid4
import asyncio
from datetime import datetime
from io import BytesIO

from ..core.database import db_manager
from ..core.config import settings
from .layout_analysis.surya_processor import SuryaDocumentProcessor
from ..db.crud import get_document_crud


class DocumentService:
    def __init__(self):
        # MinIO configuration
        self.minio_endpoint = settings.MINIO_ENDPOINT
        self.minio_access_key = settings.MINIO_ACCESS_KEY
        self.minio_secret_key = settings.MINIO_SECRET_KEY
        self.minio_secure = settings.MINIO_SECURE
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._minio_client = None
    
    @property
    def minio_client(self):
        """Lazy initialization of MinIO client"""
        if self._minio_client is None:
            self._minio_client = Minio(
                endpoint=self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=self.minio_secure
            )
            self._ensure_bucket_exists()
        from ..db.crud import get_document_crud
        return self._minio_client

    def _ensure_bucket_exists(self):
        """Ensure the MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    def _get_mime_type(self, file_content: bytes, filename: str) -> str:
        """Detect MIME type of file"""
        try:
            # Use mimetypes for MIME type detection
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                return mime_type
        except:
            pass
        
        # Fallback to basic detection based on file extension
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_mapping = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'txt': 'text/plain'
        }
        return mime_mapping.get(ext, 'application/octet-stream')

    def _generate_minio_path(self, user_id: str, filename: str) -> str:
        """Generate a unique path for the file in MinIO"""
        file_id = str(uuid4())
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        ext = filename.split('.')[-1] if '.' in filename else ''
        return f"{user_id}/{timestamp}/{file_id}.{ext}" if ext else f"{user_id}/{timestamp}/{file_id}"

    def _check_document_exists_by_hash(self, file_hash: str) -> Optional[str]:
        """Check if document already exists by hash"""
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM documents WHERE document_hash = %s",
                        (file_hash,)
                    )
                    result = cursor.fetchone()
                    return str(result[0]) if result else None
        except Exception as e:
            print(f"Error checking document hash: {e}")
            return None

    async def upload_document(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Upload document to MinIO and save metadata to database
        """
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Validate file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
                )

            # Calculate file hash
            file_hash = self._calculate_file_hash(file_content)

            # Check if document already exists
            existing_doc_id = self._check_document_exists_by_hash(file_hash)
            if existing_doc_id:
                return {
                    "document_id": existing_doc_id,
                    "message": "Document already exists",
                    "status": "duplicate"
                }

            # Get MIME type
            mime_type = self._get_mime_type(file_content, file.filename or "unknown")

            # Validate file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/gif',
                'text/plain'
            ]

            if mime_type not in allowed_types:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {mime_type}"
                )

            # Generate MinIO path
            minio_path = self._generate_minio_path(user_id, file.filename or "unknown")

            # Upload to MinIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=minio_path,
                data=BytesIO(file_content),
                length=file_size,
                content_type=mime_type
            )

            # Create document record in database
            document_id = str(uuid4())
            now = datetime.utcnow()

            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Insert document
                    cursor.execute("""
                        INSERT INTO documents (
                            id, original_filename, file_path_minio, file_size, 
                            mime_type, document_hash, uploaded_by_user_id, upload_timestamp, 
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        document_id, file.filename or "unknown", minio_path,
                        file_size, mime_type, file_hash, user_id, now, now, now
                    ))

                    # Create processing record
                    processing_id = str(uuid4())
                    cursor.execute("""
                        INSERT INTO document_processing (id, document_id, processing_status)
                        VALUES (%s, %s, %s)
                    """, (processing_id, document_id, "pending"))

                    conn.commit()

            # Start background processing
            asyncio.create_task(self._start_document_processing(document_id))

            return {
                "document_id": document_id,
                "file_path": minio_path,
                "message": "Document uploaded successfully",
                "status": "processing",
                "file_size": file_size,
                "mime_type": mime_type
            }

        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"MinIO upload failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def _start_document_processing(self, document_id: str):
        """Background pipeline: download file, run OCR/layout, store content, update status."""
        try:
            # Mark processing
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s WHERE document_id=%s", ("processing", document_id))
                    conn.commit()

            # Get file path
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT file_path_minio, original_filename FROM documents WHERE id=%s", (document_id,))
                    row = cursor.fetchone()
            if not row:
                raise ValueError("Document not found for OCR")
            file_path_minio, original_filename = row

            # Download file to temp
            tmp_dir = os.path.join(os.getcwd(), "_proc_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            local_path = os.path.join(tmp_dir, original_filename)
            obj = self.minio_client.get_object(self.bucket_name, file_path_minio)
            try:
                with open(local_path, "wb") as f:
                    for d in obj.stream(32 * 1024):
                        f.write(d)
            finally:
                obj.close(); obj.release_conn()

            # Run Surya OCR + layout
            processor = SuryaDocumentProcessor(preprocess_scanned=True)
            pages: List[List[Dict[str, Any]]] = processor.process_document(local_path)

            # Aggregate
            text_parts: List[str] = []
            layout_sections: List[Dict[str, Any]] = []
            confidences: List[float] = []
            has_tables = False
            has_images = False
            for page_num, page in enumerate(pages, start=1):
                for elem in page:
                    txt = elem.get("extracted_text") or ""
                    if txt:
                        text_parts.append(txt)
                    conf = elem.get("confidence")
                    if conf is not None:
                        confidences.append(conf)
                    etype = (elem.get("element_type") or "").lower()
                    if "table" in etype:
                        has_tables = True
                    if any(k in etype for k in ["image", "figure"]):
                        has_images = True
                    layout_sections.append({
                        "page_number": page_num,
                        "element_type": elem.get("element_type"),
                        "bounding_box": elem.get("bounding_box"),
                        "text": txt,
                        "confidence": conf
                    })

            full_text = "\n".join(text_parts) if text_parts else None
            avg_conf = sum(confidences)/len(confidences) if confidences else None

            # Persist document_content
            try:
                crud = get_document_crud()
                crud.save_document_content(
                    document_id=document_id,
                    extracted_text=full_text,
                    layout_sections=layout_sections,
                    ocr_confidence_score=avg_conf,
                    has_tables=has_tables,
                    has_images=has_images
                )
            except Exception as ce:
                print(f"Warning: could not save document_content for {document_id}: {ce}")

            # Mark completed
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, ocr_completed_at=%s WHERE document_id=%s", ("completed", datetime.utcnow(), document_id))
                    conn.commit()
        except Exception as e:
            # Mark failed
            err = {"message": str(e), "ts": datetime.utcnow().isoformat()}
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", ("failed", str(err), document_id))
                    conn.commit()

    def get_document_download_url(self, file_path: str, expires_in_hours: int = 1) -> str:
        """Generate a presigned URL for downloading the document"""
        try:
            from datetime import timedelta
            url = self.minio_client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                expires=timedelta(hours=expires_in_hours)
            )
            return url
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")

    def delete_document(self, file_path: str, document_id: str):
        """Delete document from MinIO and database"""
        try:
            # Delete from MinIO
            self.minio_client.remove_object(self.bucket_name, file_path)

            # Delete from database (CASCADE will handle related records)
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
                    conn.commit()

        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


# Initialize service instance
document_service = DocumentService()