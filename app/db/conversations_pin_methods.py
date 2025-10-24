from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
import logging

from .models import Conversation as ConversationModel

logger = logging.getLogger(__name__)


def toggle_pin(db_manager, conversation_id: UUID) -> Optional[ConversationModel]:
    """Toggle the pin status of a conversation"""
    try:
        query = """
            UPDATE conversations
            SET is_pinned = NOT COALESCE(is_pinned, FALSE), updated_at = %s
            WHERE id = %s
            RETURNING *
        """
        params = (datetime.now(timezone.utc), conversation_id)
        result = db_manager.execute_one(query, params)
        if result:
            return ConversationModel(**dict(result))
        return None
    except Exception as e:
        logger.error(f"Error toggling pin status: {e}")
        raise


def get_pinned_conversations(db_manager, user_id: UUID, limit: int = 10) -> List[ConversationModel]:
    """Get all pinned conversations for a user"""
    try:
        query = """
            SELECT * FROM conversations
            WHERE user_id = %s AND is_pinned = TRUE
            ORDER BY updated_at DESC
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit), fetch=True)
        return [ConversationModel(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Error getting pinned conversations: {e}")
        raise
