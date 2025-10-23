from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
import asyncpg
from app.core.config import settings
from app.db.models import UserDocumentSelection
import logging

logger = logging.getLogger(__name__)

class DocumentSelectionService:
    """Service for managing user document selections in Knowledge Base mode"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
    
    async def get_connection(self):
        """Get database connection"""
        return await asyncpg.connect(self.db_url)
    
    async def save_user_document_selection(self, user_id: UUID, document_ids: List[str]) -> UserDocumentSelection:
        """Save or update user's document selection"""
        try:
            conn = await self.get_connection()
            try:
                # Check if user already has a selection record
                existing = await conn.fetchrow(
                    "SELECT id, created_at FROM user_document_selections WHERE user_id = $1",
                    user_id
                )
                
                now = datetime.utcnow()
                
                if existing:
                    # Update existing record
                    await conn.execute(
                        """UPDATE user_document_selections 
                           SET selected_document_ids = $1, updated_at = $2 
                           WHERE user_id = $3""",
                        document_ids, now, user_id
                    )
                    selection_id = existing['id']
                    created_at = existing['created_at']
                else:
                    # Create new record
                    selection_id = uuid4()
                    await conn.execute(
                        """INSERT INTO user_document_selections 
                           (id, user_id, selected_document_ids, created_at, updated_at)
                           VALUES ($1, $2, $3, $4, $5)""",
                        selection_id, user_id, document_ids, now, now
                    )
                    created_at = now
                
                logger.info(f"Saved document selection for user {user_id}: {document_ids}")
                
                return UserDocumentSelection(
                    id=selection_id,
                    user_id=user_id,
                    selected_document_ids=document_ids,
                    created_at=created_at,
                    updated_at=now
                )
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error saving document selection for user {user_id}: {str(e)}")
            raise
    
    async def get_user_document_selection(self, user_id: UUID) -> Optional[UserDocumentSelection]:
        """Get user's document selection"""
        try:
            conn = await self.get_connection()
            try:
                row = await conn.fetchrow(
                    """SELECT id, user_id, selected_document_ids, created_at, updated_at 
                       FROM user_document_selections WHERE user_id = $1""",
                    user_id
                )
                
                if row:
                    return UserDocumentSelection(
                        id=row['id'],
                        user_id=row['user_id'],
                        selected_document_ids=row['selected_document_ids'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                
                return None
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error getting document selection for user {user_id}: {str(e)}")
            raise
    
    async def clear_user_document_selection(self, user_id: UUID) -> bool:
        """Clear user's document selection"""
        try:
            conn = await self.get_connection()
            try:
                result = await conn.execute(
                    "DELETE FROM user_document_selections WHERE user_id = $1",
                    user_id
                )
                
                logger.info(f"Cleared document selection for user {user_id}")
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error clearing document selection for user {user_id}: {str(e)}")
            raise

# Global instance
document_selection_service = DocumentSelectionService()
