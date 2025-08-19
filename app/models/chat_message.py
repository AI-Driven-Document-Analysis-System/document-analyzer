from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    message_id: str
    conversation_id: str
    role: str  # user, assistant
    content: str
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

class ConversationSource(BaseModel):
    document_id: str
    filename: str
    document_type: str
    relevance_score: float
    chunk_content: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    sources: List[ConversationSource]
    context_used: bool
    processing_time: Optional[float] = None

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    title: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()