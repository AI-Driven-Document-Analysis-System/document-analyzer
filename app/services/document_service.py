import os
import hashlib
import magic
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple, Optional
from uuid import uuid4
import asyncio
from datetime import datetime

from db.crud import document_crud
from schemas.document_schemas import DocumentCreate, DocumentProcessingCreate

class DocumentService:
    def __init__(self):
        # MinIO configuration - adjust these based on your setup
        self.minio_client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "False").lower() == "true"
        )
        self.bucket_name = os.getenv("MINIO_BUCKET", "documents")
        self._ensure_bucket_exists()
    
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
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file_content)
            return mime_type
        except:
            # Fallback to basic detection based on file extension
            ext = filename.lower().split('.')[-1]
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
    
    async def upload_document(self, file: UploadFile, user_id: str, db: Session) -> Tuple[str, str]:
        """
        Upload document to MinIO and save metadata to database
        Returns: (document_id, file_path)
        """
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size (e.g., max 50MB)
            max_size = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
            if file_size > max_size:
                raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {max_size/1024/1024}MB")
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_content)
            
            # Check if document already exists
            existing_doc_id = document_crud.check_document_exists_by_hash(db, file_hash)
            if existing_doc_id:
                return existing_doc_id, "Document already exists"
            
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
                raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime_type}")
            
            # Generate MinIO path
            minio_path = self._generate_minio_path(user_id, file.filename or "unknown")
            
            # Upload to MinIO
            from io import BytesIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=minio_path,
                data=BytesIO(file_content),
                length=file_size,
                content_type=mime_type
            )
            
            # Create document record
            document_data = DocumentCreate(
                original_filename=file.filename or "unknown",
                file_path_minio=minio_path,
                file_size=file_size,
                mime_type=mime_type,
                document_hash=file_hash,
                user_id=user_id
            )
            
            document_id = document_crud.create_document(db, document_data)
            
            # Create processing record
            processing_data = DocumentProcessingCreate(
                document_id=document_id,
                processing_status="uploaded"
            )
            
            document_crud.create_document_processing(db, processing_data)
            
            # Start background processing (implement this based on your processing pipeline)
            await self._start_document_processing(document_id, db)
            
            return document_id, minio_path
            
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"MinIO upload failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def _start_document_processing(self, document_id: str, db: Session):
        """
        Start background document processing
        This is a placeholder - implement your actual processing pipeline
        """
        # Update status to processing
        document_crud.update_processing_status(db, document_id, "processing")
        
        # Simulate processing delay (replace with actual processing logic)
        await asyncio.sleep(2)
        
        try:
            # Your processing logic here:
            # 1. OCR for images/scanned PDFs
            # 2. Text extraction
            # 3. Classification
            # 4. Summarization
            # 5. Embedding generation
            # 6. Indexing
            
            # For now, just mark as completed
            document_crud.update_processing_status(db, document_id, "completed")
            
        except Exception as e:
            # Mark as failed with error details
            error_details = {"message": str(e), "timestamp": datetime.utcnow().isoformat()}
            document_crud.update_processing_status(db, document_id, "failed", error_details)
    
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
    
    def delete_document(self, file_path: str, document_id: str, db: Session):
        """Delete document from MinIO and database"""
        try:
            # Delete from MinIO
            self.minio_client.remove_object(self.bucket_name, file_path)
            
            # Delete from database (CASCADE will handle related records)
            from sqlalchemy import text
            query = text("DELETE FROM documents WHERE id = :document_id")
            db.execute(query, {"document_id": document_id})
            db.commit()
            
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

# Initialize service instance
document_service = DocumentService()