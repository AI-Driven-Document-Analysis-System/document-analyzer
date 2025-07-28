from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    original_filename: str
    file_size: int
    mime_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID
    file_path_minio: str
    document_hash: Optional[str]
    page_count: Optional[int]
    language_detected: Optional[str]
    upload_timestamp: datetime
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentProcessingResponse(BaseModel):
    id: UUID
    document_id: UUID
    processing_status: str
    processing_errors: Optional[Dict[str, Any]]
    ocr_completed_at: Optional[datetime]
    classification_completed_at: Optional[datetime]
    summarization_completed_at: Optional[datetime]
    indexing_completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    processing: DocumentProcessingResponse
    message: str
