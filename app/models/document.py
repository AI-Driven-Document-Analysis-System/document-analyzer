from sqlalchemy import Column, String, BigInteger, Integer, DateTime, UUID, Text, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    file_path_minio = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    document_hash = Column(String(64), unique=True)
    page_count = Column(Integer)
    language_detected = Column(String(10))
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by_user_id = Column(PostgresUUID(as_uuid=True))
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="documents")
    processing = relationship("DocumentProcessing", back_populates="document", uselist=False)
    content = relationship("DocumentContent", back_populates="document", uselist=False)
    classifications = relationship("DocumentClassification", back_populates="document")
    summaries = relationship("DocumentSummary", back_populates="document")

class DocumentProcessing(Base):
    __tablename__ = "document_processing"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    processing_status = Column(String(50), nullable=False)
    processing_errors = Column(JSONB)
    ocr_completed_at = Column(DateTime(timezone=True))
    classification_completed_at = Column(DateTime(timezone=True))
    summarization_completed_at = Column(DateTime(timezone=True))
    indexing_completed_at = Column(DateTime(timezone=True))

    # Relationships
    document = relationship("Document", back_populates="processing")

class DocumentContent(Base):
    __tablename__ = "document_content"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    extracted_text = Column(Text)
    searchable_content = Column(Text)
    layout_sections = Column(JSONB)
    entities_extracted = Column(JSONB)
    ocr_confidence_score = Column(DECIMAL(5, 4))
    has_tables = Column(Boolean, default=False)
    has_images = Column(Boolean, default=False)

    # Relationships
    document = relationship("Document", back_populates="content")

class DocumentClassification(Base):
    __tablename__ = "document_classifications"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    document_type = Column(String(50), nullable=False)
    confidence_score = Column(DECIMAL(5, 4), nullable=False)
    model_version = Column(String(20))
    classified_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="classifications")

class DocumentSummary(Base):
    __tablename__ = "document_summaries"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    summary_text = Column(Text, nullable=False)
    key_points = Column(JSONB)
    model_version = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="summaries")
