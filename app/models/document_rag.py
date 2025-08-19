from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    filename: Optional[str] = None
    upload_date: Optional[str] = None
    user_id: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None

class DocumentSection(BaseModel):
    type: str  # header, paragraph, table, etc.
    text: str
    page: Optional[int] = None
    bbox: Optional[List[float]] = None

class LayoutData(BaseModel):
    sections: List[DocumentSection]
    tables: Optional[List[Dict]] = None
    images: Optional[List[Dict]] = None

class Document(BaseModel):
    id: str
    text: Optional[str] = None
    layout_data: Optional[LayoutData] = None
    metadata: DocumentMetadata
    processing_status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None