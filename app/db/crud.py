from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import hashlib
import json
from .models import User, Document, DocumentProcessing, DocumentContent
from ..core.database import get_db
from ..core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_user(self, email: str, password: str = None, first_name: str = None, last_name: str = None, 
                   google_id: str = None, is_oauth_user: bool = False) -> Optional[User]:
        """Create a new user"""
        try:
            user_id = uuid4()
            password_hash = get_password_hash(password) if password else None
            
            query = """
                INSERT INTO users (id, email, password_hash, first_name, last_name, google_id, is_oauth_user, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, email, password_hash, first_name, last_name, 
                          is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
            """
            
            now = datetime.utcnow()
            params = (user_id, email, password_hash, first_name, last_name, google_id, is_oauth_user, now, now)
            
            result = self.db.execute_one(query, params)
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            query = """
                SELECT id, email, password_hash, first_name, last_name, 
                       is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
                FROM users WHERE email = %s
            """
            result = self.db.execute_one(query, (email,))
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        try:
            query = """
                SELECT id, email, password_hash, first_name, last_name, 
                       is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
                FROM users WHERE id = %s
            """
            result = self.db.execute_one(query, (user_id,))
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = self.get_user_by_email(email)
            if user and verify_password(password, user.password_hash):
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Update user information"""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in kwargs.items():
                if key in ['first_name', 'last_name', 'is_email_verified', 'email_verification_token', 'google_id', 'is_oauth_user']:
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            if not set_clauses:
                return self.get_user_by_id(user_id)
            
            set_clauses.append("updated_at = %s")
            params.append(datetime.utcnow())
            params.append(user_id)
            
            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING id, email, password_hash, first_name, last_name, 
                          is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
            """
            
            result = self.db.execute_one(query, params)
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    def change_user_email(self, user_id: UUID, new_email: str, password: str) -> Optional[User]:
        """Change user email after verifying current password"""
        try:
            # First verify the current password
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            if not verify_password(password, user.password_hash):
                return None
            
            # Check if new email already exists
            existing_user = self.get_user_by_email(new_email)
            if existing_user and existing_user.id != user_id:
                return None
            
            # Update email
            query = """
                UPDATE users 
                SET email = %s, updated_at = %s
                WHERE id = %s
                RETURNING id, email, password_hash, first_name, last_name, 
                          is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
            """
            
            now = datetime.utcnow()
            params = (new_email, now, user_id)
            
            result = self.db.execute_one(query, params)
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error changing user email: {e}")
            raise

    def change_user_password(self, user_id: UUID, current_password: str, new_password: str) -> Optional[User]:
        """Change user password after verifying current password"""
        try:
            # First verify the current password
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            if not verify_password(current_password, user.password_hash):
                return None
            
            # Hash new password
            new_password_hash = get_password_hash(new_password)
            
            # Update password
            query = """
                UPDATE users 
                SET password_hash = %s, updated_at = %s
                WHERE id = %s
                RETURNING id, email, password_hash, first_name, last_name, 
                          is_email_verified, email_verification_token, google_id, is_oauth_user, created_at, updated_at
            """
            
            now = datetime.utcnow()
            params = (new_password_hash, now, user_id)
            
            result = self.db.execute_one(query, params)
            
            if result:
                return User(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error changing user password: {e}")
            raise

class DocumentCRUD:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_document(self, user_id: UUID, filename: str, file_path: str, 
                       file_size: int, mime_type: str, file_content: bytes = None) -> Optional[Document]:
        """Create a new document record"""
        try:
            document_id = uuid4()
            
            # Generate document hash
            document_hash = hashlib.sha256(file_content or b'').hexdigest() if file_content else None
            
            query = """
                INSERT INTO documents (
                    id, original_filename, file_path_minio, file_size, mime_type, 
                    document_hash, user_id, upload_timestamp, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            
            now = datetime.utcnow()
            params = (
                document_id, filename, file_path, file_size, mime_type,
                document_hash, user_id, now, now, now
            )
            
            result = self.db.execute_one(query, params)
            
            if result:
                # Create initial processing record
                self.create_document_processing(document_id)
                return Document(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    def create_document_processing(self, document_id: UUID) -> Optional[DocumentProcessing]:
        """Create initial document processing record"""
        try:
            processing_id = uuid4()
            
            query = """
                INSERT INTO document_processing (id, document_id, processing_status)
                VALUES (%s, %s, %s)
                RETURNING *
            """
            
            params = (processing_id, document_id, "pending")
            result = self.db.execute_one(query, params)
            
            if result:
                return DocumentProcessing(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error creating document processing: {e}")
            raise
    
    def get_user_documents(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Document]:
        """Get documents for a user"""
        try:
            query = """
                SELECT * FROM documents 
                WHERE user_id = %s 
                ORDER BY upload_timestamp DESC 
                LIMIT %s OFFSET %s
            """
            
            results = self.db.execute_query(query, (user_id, limit, offset), fetch=True)
            
            return [Document(**dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            raise
    
    def get_document_by_id(self, document_id: UUID, user_id: UUID = None) -> Optional[Document]:
        """Get document by ID"""
        try:
            query = "SELECT * FROM documents WHERE id = %s"
            params = [document_id]
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            result = self.db.execute_one(query, params)
            
            if result:
                return Document(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            raise
    
    def save_document_content(self, document_id: UUID, extracted_text: str = None, 
                            searchable_content: str = None, layout_sections: Dict[str, Any] = None,
                            entities_extracted: Dict[str, Any] = None, ocr_confidence_score: float = None,
                            has_tables: bool = False, has_images: bool = False) -> Optional[DocumentContent]:
        """Save or update document content after OCR processing"""
        try:
            content_id = uuid4()
            
            # First, try to add missing columns if they don't exist
            try:
                self.db.execute_query("""
                    ALTER TABLE document_content 
                    ADD COLUMN IF NOT EXISTS entities_extracted JSONB
                """)
                self.db.execute_query("""
                    ALTER TABLE document_content 
                    ADD COLUMN IF NOT EXISTS ocr_confidence_score DECIMAL(5,4)
                """)
                self.db.execute_query("""
                    ALTER TABLE document_content 
                    ADD COLUMN IF NOT EXISTS has_tables BOOLEAN DEFAULT FALSE
                """)
                self.db.execute_query("""
                    ALTER TABLE document_content 
                    ADD COLUMN IF NOT EXISTS has_images BOOLEAN DEFAULT FALSE
                """)
            except Exception as e:
                logger.warning(f"Could not add missing columns (they may already exist): {e}")
            
            # Simple INSERT - remove ON CONFLICT since constraint doesn't exist
            query = """
                INSERT INTO document_content (
                    id, document_id, extracted_text, searchable_content, layout_sections,
                    entities_extracted, ocr_confidence_score, has_tables, has_images
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert dict objects to JSON strings for database storage
            layout_sections_json = json.dumps(layout_sections) if layout_sections else None
            entities_extracted_json = json.dumps(entities_extracted) if entities_extracted else None
            
            params = (
                content_id, document_id, extracted_text, searchable_content,
                layout_sections_json, entities_extracted_json, ocr_confidence_score,
                has_tables, has_images
            )
            
            # Execute INSERT without expecting a result
            self.db.execute_query(query, params)
            
            # Return success indicator
            return True
            
        except Exception as e:
            logger.error(f"Error saving document content: {e}")
            raise
    
    def save_document_classification(self, document_id: UUID, document_type: str, confidence_score: float = 1.0, model_version: str = None) -> bool:
        """Insert or update document classification for a document."""
        from datetime import datetime
        try:
            # Check if classification exists
            existing = self.db.execute_one(
                "SELECT id FROM document_classifications WHERE document_id = %s",
                (document_id,)
            )
            now = datetime.utcnow()
            if existing:
                query = (
                    """
                    UPDATE document_classifications
                    SET document_type = %s,
                        confidence_score = %s,
                        model_version = %s,
                        classified_at = %s
                    WHERE document_id = %s
                    """
                )
                params = (document_type, confidence_score, model_version, now, document_id)
            else:
                query = (
                    """
                    INSERT INTO document_classifications (
                        id, document_id, document_type, confidence_score, model_version, classified_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                )
                from uuid import uuid4
                params = (str(uuid4()), document_id, document_type, confidence_score, model_version, now)
            self.db.execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Error saving document classification: {e}")
            return False

# Initialize CRUD instances
def get_user_crud():
    return UserCRUD(get_db())

def get_document_crud():
    return DocumentCRUD(get_db())



