from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class User:
    id: UUID
    email: str
    password_hash: Optional[str] = None  # Optional for OAuth users
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_email_verified: bool = False
    email_verification_token: Optional[str] = None
    google_id: Optional[str] = None  # Google OAuth ID
    is_oauth_user: bool = False  # Flag for OAuth users
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Document:
    id: UUID
    original_filename: str
    file_path_minio: str
    file_size: int
    mime_type: str
    document_hash: str
    page_count: Optional[int] = None
    language_detected: Optional[str] = None
    upload_timestamp: datetime = None
    uploaded_by_user_id: UUID = None
    user_id: UUID = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class DocumentProcessing:
    id: UUID
    document_id: UUID
    processing_status: ProcessingStatus
    processing_errors: Optional[Dict[str, Any]] = None
    ocr_completed_at: Optional[datetime] = None
    classification_completed_at: Optional[datetime] = None
    summarization_completed_at: Optional[datetime] = None
    indexing_completed_at: Optional[datetime] = None

@dataclass
class DocumentContent:
    id: UUID
    document_id: UUID
    extracted_text: Optional[str] = None
    searchable_content: Optional[str] = None
    layout_sections: Optional[Dict[str, Any]] = None
    entities_extracted: Optional[Dict[str, Any]] = None
    ocr_confidence_score: Optional[float] = None
    has_tables: bool = False
    has_images: bool = False

@dataclass
class DocumentClassification:
    id: UUID
    document_id: UUID
    document_type: str
    confidence_score: float
    model_version: Optional[str] = None
    classified_at: datetime = None

@dataclass
class DocumentSummary:
    id: UUID
    document_id: UUID
    summary_text: str
    key_points: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    created_at: datetime = None

@dataclass
class SubscriptionPlan:
    id: UUID
    name: str
    price_monthly: float
    price_yearly: Optional[float] = None
    features: Dict[str, Any] = None
    is_active: bool = True
    created_at: datetime = None

@dataclass
class UserSubscription:
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    started_at: datetime
    expires_at: Optional[datetime] = None
    auto_renew: bool = True
    created_at: datetime = None

@dataclass
class Conversation:
    id: UUID
    user_id: UUID
    title: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class ChatMessage:
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
