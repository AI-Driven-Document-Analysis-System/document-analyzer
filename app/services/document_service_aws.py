import os
import json
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
from dotenv import load_dotenv
import threading

from ..core.database import db_manager
from ..core.config import settings
from .ocr_service_aws_only import OCRService, OCRProvider
from ..db.crud import get_document_crud
from .document_embedding_service import document_embedding_service


class DocumentServiceAWS:
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
        return self._minio_client
    def _ensure_bucket_exists(self):
        """Ensure the MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise
    
    def _upload_to_minio(self, minio_path: str, file_content: bytes, file_size: int, mime_type: str):
        """Upload file to MinIO - thread-safe helper method"""
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=minio_path,
            data=BytesIO(file_content),
            length=file_size,
            content_type=mime_type
        )
    
    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
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

    def _check_document_exists_by_hash(self, file_hash: str, user_id: str) -> Optional[str]:
        """Check if a user's document already exists by hash (per-user deduplication)"""
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM documents WHERE document_hash = %s AND user_id = %s",
                        (file_hash, user_id)
                    )
                    result = cursor.fetchone()
                    return str(result[0]) if result else None
        except Exception as e:
            print(f"Error checking document hash: {e}")
            return None

    async def upload_document(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Upload document to MinIO and save metadata to database - optimized for performance
        """
        try:
            print(f"DEBUG - Starting upload for user: {user_id}")
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            print(f"DEBUG - File size: {file_size} bytes")

            # Validate file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
                )

            # Optimize: Run CPU-intensive operations in thread pool
            loop = asyncio.get_event_loop()
            
            # Calculate file hash in thread pool (non-blocking)
            print(f"DEBUG - Calculating file hash...")
            file_hash = await loop.run_in_executor(None, self._calculate_file_hash, file_content)
            print(f"DEBUG - File hash calculated: {file_hash[:16]}...")

            # Check if document already exists (optimized with new index)
            print(f"DEBUG - Checking for existing document...")
            existing_doc_id = await loop.run_in_executor(None, self._check_document_exists_by_hash, file_hash, user_id)
            if existing_doc_id:
                print(f"DEBUG - Document already exists: {existing_doc_id}")
                return {
                    "document_id": existing_doc_id,
                    "message": "Document already exists",
                    "status": "duplicate"
                }

            # Get MIME type
            print(f"DEBUG - Getting MIME type...")
            mime_type = self._get_mime_type(file_content, file.filename or "unknown")
            print(f"DEBUG - MIME type: {mime_type}")

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
                print(f"DEBUG - Unsupported file type: {mime_type}")
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {mime_type}"
                )

            # Generate MinIO path
            print(f"DEBUG - Generating MinIO path...")
            minio_path = self._generate_minio_path(user_id, file.filename or "unknown")
            print(f"DEBUG - MinIO path: {minio_path}")

            # Upload to MinIO in thread pool (non-blocking)
            print(f"DEBUG - Uploading to MinIO...")
            await loop.run_in_executor(None, self._upload_to_minio, minio_path, file_content, file_size, mime_type)
            print(f"DEBUG - MinIO upload successful")

            # Create document record in database
            document_id = str(uuid4())
            now = datetime.utcnow()

            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Insert document
                    cursor.execute("""
                        INSERT INTO documents (
                            id, original_filename, file_path_minio, file_size,
                            mime_type, document_hash, user_id,uploaded_by_user_id, upload_timestamp,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        document_id, file.filename or "unknown", minio_path,
                        file_size, mime_type, file_hash, user_id, user_id, now, now, now
                    ))

                    # Create processing record
                    processing_id = str(uuid4())
                    cursor.execute("""
                        INSERT INTO document_processing (id, document_id, processing_status)
                        VALUES (%s, %s, %s)
                    """, (processing_id, document_id, "pending"))

                    conn.commit()

            # Start background processing with AWS Textract
            asyncio.create_task(self._start_document_processing_aws(document_id))

            print(f"DEBUG - About to return result with file_size: {file_size}")
            return {
                "document_id": document_id,
                "file_path": minio_path,
                "message": "Document uploaded successfully - processing with AWS Textract",
                "status": "processing",
                "file_size": file_size,
                "mime_type": mime_type
            }

        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"MinIO upload failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def _start_document_processing_aws(self, document_id: str):
        """Background pipeline: download file, run AWS Textract OCR, store content, update status."""
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

            # Run OCR processing (AWS Textract or Surya fallback)
            print(f"Starting OCR processing for document {document_id}")
            
            # Ensure environment variables are loaded in background task
            # Get the project root directory and load .env file explicitly
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, '.env')
            print(f"DEBUG - Loading .env from: {env_path}")
            print(f"DEBUG - .env file exists: {os.path.exists(env_path)}")
            
            load_dotenv(dotenv_path=env_path, override=True)
            
            # Force AWS Textract if credentials are available
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            ocr_provider = os.getenv("OCR_PROVIDER", "aws_textract")
            
            # Debug logging
            print(f"DEBUG - AWS_ACCESS_KEY_ID: {'Found' if aws_access_key else 'Missing'}")
            print(f"DEBUG - AWS_SECRET_ACCESS_KEY: {'Found' if aws_secret_key else 'Missing'}")
            print(f"DEBUG - OCR_PROVIDER: {ocr_provider}")
            
            if aws_access_key and aws_secret_key:
                print(f"AWS credentials detected, using AWS Textract")
                ocr_service = OCRService(provider=OCRProvider.AWS_TEXTRACT)
            else:
                raise Exception("AWS Textract credentials required")
                
            # Process document with AWS OCR
            ocr_result = ocr_service.process_document(local_path, document_id)
            
            # Extract results from AWS OCR service
            full_text = ocr_result.get('extracted_text')
            searchable_content = ocr_result.get('searchable_content')
            layout_sections = ocr_result.get('layout_sections', {})
            avg_conf = ocr_result.get('ocr_confidence_score')
            has_tables = ocr_result.get('has_tables', False)
            has_images = ocr_result.get('has_images', False)
            provider_used = ocr_result.get('provider', 'aws_textract')
            
            print(f"OCR processing completed using {provider_used} provider")
            print(f"Extracted {len(full_text) if full_text else 0} characters of text")

            # Clean up temporary file
            try:
                os.remove(local_path)
            except:
                pass

            # Persist document_content
            try:
                crud = get_document_crud()
                crud.save_document_content(
                    document_id=document_id,
                    extracted_text=full_text,
                    searchable_content=searchable_content,
                    layout_sections=layout_sections,
                    ocr_confidence_score=avg_conf,
                    has_tables=has_tables,
                    has_images=has_images
                )
                print(f"Document content saved successfully for {document_id}")
                
                # Start automatic embedding in background thread
                def embed_document_background():
                    try:
                        # Import inside thread to ensure module availability
                        import sys
                        import os
                        app_dir = os.path.join(os.path.dirname(__file__), '..')
                        if app_dir not in sys.path:
                            sys.path.append(app_dir)
                        
                        from services.document_embedding_service import document_embedding_service
                        
                        print(f"Starting automatic embedding for document {document_id}")
                        result = document_embedding_service.embed_document(document_id)
                        if result['success']:
                            print(f"Document {document_id} embedded successfully: {result['chunks_created']} chunks created")
                        else:
                            print(f"Document {document_id} embedding failed: {result['error']}")
                    except Exception as e:
                        print(f"Background embedding error for {document_id}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # Start embedding in background thread (non-blocking)
                embedding_thread = threading.Thread(target=embed_document_background)
                embedding_thread.daemon = True
                embedding_thread.start()
                
            except Exception as ce:
                print(f"Warning: could not save document_content for {document_id}: {ce}")

            # Mark completed
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, ocr_completed_at=%s WHERE document_id=%s", ("completed", datetime.utcnow(), document_id))
                    conn.commit()
                    
            print(f"Document processing completed successfully for {document_id}")
            
        except Exception as e:
            # Mark failed
            print(f"Document processing failed for {document_id}: {e}")
            err = {"message": str(e), "ts": datetime.utcnow().isoformat()}
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE document_processing SET processing_status=%s, processing_errors=%s WHERE document_id=%s", ("failed", json.dumps(err), document_id))
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


# Initialize AWS-enabled service instance
document_service_aws = DocumentServiceAWS()
