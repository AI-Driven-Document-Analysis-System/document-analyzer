from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
import json
import logging

from .models import Conversation as ConversationModel, ChatMessage as ChatMessageModel
from ..core.database import get_db
from . import conversations_pin_methods

logger = logging.getLogger(__name__)


class Conversations:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, user_id: Optional[UUID] = None, title: Optional[str] = None) -> Optional[ConversationModel]:
        try:
            conversation_id = uuid4()
            # Use timezone-aware UTC datetime for global compatibility
            now = datetime.now(timezone.utc)
            query = """
                INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """
            params = (conversation_id, user_id, title, now, now)
            result = self.db.execute_one(query, params)
            if result:
                return ConversationModel(**dict(result))
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    def list(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[ConversationModel]:
        try:
            query = """
                SELECT * FROM conversations
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """
            results = self.db.execute_query(query, (user_id, limit, offset), fetch=True)
            return [ConversationModel(**dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            raise

    def list_with_message_counts(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Dict]:
        try:
            query = """
                SELECT c.*, COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN chat_messages m ON c.id = m.conversation_id 
                    AND m.role IN ('user', 'assistant')
                WHERE c.user_id = %s
                GROUP BY c.id, c.user_id, c.title, c.is_pinned, c.created_at, c.updated_at
                HAVING COUNT(m.id) > 0
                ORDER BY c.updated_at DESC
                LIMIT %s OFFSET %s
            """
            results = self.db.execute_query(query, (user_id, limit, offset), fetch=True)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error listing conversations with message counts: {e}")
            raise

    def get(self, conversation_id: UUID, user_id: Optional[UUID] = None) -> Optional[ConversationModel]:
        try:
            if user_id:
                query = "SELECT * FROM conversations WHERE id = %s AND user_id = %s"
                params = (conversation_id, user_id)
            else:
                query = "SELECT * FROM conversations WHERE id = %s"
                params = (conversation_id,)
            result = self.db.execute_one(query, params)
            if result:
                return ConversationModel(**dict(result))
            return None
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            raise

    def rename(self, conversation_id: UUID, title: str) -> Optional[ConversationModel]:
        try:
            query = """
                UPDATE conversations
                SET title = %s, updated_at = %s
                WHERE id = %s
                RETURNING *
            """
            params = (title, datetime.now(timezone.utc), conversation_id)
            result = self.db.execute_one(query, params)
            if result:
                return ConversationModel(**dict(result))
            return None
        except Exception as e:
            logger.error(f"Error renaming conversation: {e}")
            raise

    def delete(self, conversation_id: UUID) -> int:
        try:
            query = "DELETE FROM conversations WHERE id = %s"
            return self.db.execute_query(query, (conversation_id,))
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            raise

    def toggle_pin(self, conversation_id: UUID) -> Optional[ConversationModel]:
        return conversations_pin_methods.toggle_pin(self.db, conversation_id)

    def get_pinned_conversations(self, user_id: UUID, limit: int = 10) -> List[ConversationModel]:
        return conversations_pin_methods.get_pinned_conversations(self.db, user_id, limit)


class Messages:
    def __init__(self, db_manager):
        self.db = db_manager

    def add(self, conversation_id: UUID, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[ChatMessageModel]:
        try:
            message_id = uuid4()
            # Use timezone-aware UTC datetime for global compatibility
            now = datetime.now(timezone.utc)
            query = """
                INSERT INTO chat_messages (id, conversation_id, role, content, metadata, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            params = (message_id, conversation_id, role, content, json.dumps(metadata) if metadata is not None else None, now)
            result = self.db.execute_one(query, params)
            if result:
                # Bump conversation updated_at
                self.db.execute_query("UPDATE conversations SET updated_at = %s WHERE id = %s", (now, conversation_id))
                row = dict(result)
                if isinstance(row.get("metadata"), str):
                    try:
                        row["metadata"] = json.loads(row["metadata"]) if row["metadata"] else None
                    except Exception:
                        pass
                return ChatMessageModel(**row)
            return None
        except Exception as e:
            logger.error(f"Error adding chat message: {e}")
            raise

    def list(self, conversation_id: UUID, limit: int = 200, offset: int = 0) -> List[ChatMessageModel]:
        try:
            query = """
                SELECT * FROM chat_messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
                LIMIT %s OFFSET %s
            """
            results = self.db.execute_query(query, (conversation_id, limit, offset), fetch=True)
            messages: List[ChatMessageModel] = []
            for row in results:
                row_dict = dict(row)
                if isinstance(row_dict.get("metadata"), str):
                    try:
                        row_dict["metadata"] = json.loads(row_dict["metadata"]) if row_dict["metadata"] else None
                    except Exception:
                        pass
                messages.append(ChatMessageModel(**row_dict))
            return messages
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            raise

    def prune_keep_last_pairs(self, conversation_id: UUID, keep_pairs: int = 8) -> int:
        """
        Delete older messages for a conversation, keeping only the last `keep_pairs` user/assistant pairs.
        System summary messages added recently will be preserved if they are among the last kept messages.
        Returns number of deleted rows.
        """
        try:
            # Fetch all ids ordered by time
            fetch_query = """
                SELECT id FROM chat_messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """
            rows = self.db.execute_query(fetch_query, (conversation_id,), fetch=True)
            ids = [row["id"] for row in rows]

            keep_count = keep_pairs * 2
            if len(ids) <= keep_count:
                return 0

            to_delete = ids[: len(ids) - keep_count]
            deleted = 0
            # Delete in small batches to avoid parameter limits
            for i in range(0, len(to_delete), 100):
                batch = to_delete[i:i+100]
                del_query = "DELETE FROM chat_messages WHERE id = ANY(%s)"
                # Some drivers require tuple(list) for arrays
                self.db.execute_query(del_query, (batch,))
                deleted += len(batch)
            return deleted
        except Exception as e:
            logger.error(f"Error pruning chat messages: {e}")
            raise

    def delete_by_conversation(self, conversation_id: UUID) -> int:
        """
        Delete all messages for a specific conversation.
        Returns number of deleted rows.
        """
        try:
            query = "DELETE FROM chat_messages WHERE conversation_id = %s"
            return self.db.execute_query(query, (conversation_id,))
        except Exception as e:
            logger.error(f"Error deleting messages for conversation {conversation_id}: {e}")
            raise


def get_conversations() -> Conversations:
    return Conversations(get_db())


def get_messages() -> Messages:
    return Messages(get_db()) 