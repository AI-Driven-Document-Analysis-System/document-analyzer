from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"
    LLAMA = "llama"


class MemoryType(str, Enum):
    """Conversation memory types"""
    WINDOW = "window"
    SUMMARY = "summary"


class SearchMode(str, Enum):
    """Search mode types"""
    STANDARD = "standard"
    REPHRASE = "rephrase"
    MULTIPLE_QUERIES = "multiple_queries"


class ChatMessageRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User ID for filtering documents")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM configuration override")
    memory_type: MemoryType = Field(MemoryType.WINDOW, description="Memory type for conversation")
    search_mode: SearchMode = Field(SearchMode.STANDARD, description="Search mode for query processing")
    selected_document_ids: Optional[List[str]] = Field(None, description="List of document IDs to search within (Knowledge Base mode)")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class DocumentIndexRequest(BaseModel):
    """Request model for document indexing"""
    id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Document text content")
    filename: Optional[str] = Field(None, description="Original filename")
    user_id: Optional[str] = Field(None, description="User ID who owns the document")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class DocumentIndexResponse(BaseModel):
    """Response model for document indexing"""
    status: str = Field(..., description="Indexing status")
    document_id: str = Field(..., description="Document ID")
    chunk_ids: List[str] = Field(..., description="IDs of created chunks")
    chunk_count: int = Field(..., description="Number of chunks created")
    message: str = Field(..., description="Status message")


class DocumentSearchRequest(BaseModel):
    """Request model for document search"""
    query: str = Field(..., description="Search query")
    k: int = Field(4, ge=1, le=20, description="Number of results to return")
    user_id: Optional[str] = Field(None, description="User ID for filtering results")


class DocumentSearchResponse(BaseModel):
    """Response model for document search"""
    query: str = Field(..., description="Original search query")
    documents: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_time: float = Field(..., description="Search execution time in seconds")


class ConversationHistoryRequest(BaseModel):
    """Request model for conversation history"""
    conversation_id: str = Field(..., description="Conversation ID")


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    message_count: int = Field(..., description="Number of messages")
    created_at: Optional[datetime] = Field(None, description="Conversation creation time")
    last_updated: Optional[datetime] = Field(None, description="Last message time")


class SystemStatsResponse(BaseModel):
    """Response model for system statistics"""
    initialized: bool = Field(..., description="Service initialization status")
    active_chat_engines: int = Field(..., description="Number of active chat engines")
    vectorstore: Dict[str, Any] = Field(..., description="Vector database statistics")
    config: Dict[str, Any] = Field(..., description="Current configuration")
    timestamp: datetime = Field(..., description="Stats timestamp")


class LLMConfigRequest(BaseModel):
    """Request model for LLM configuration"""
    provider: LLMProvider = Field(..., description="LLM provider")
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Generation temperature")
    streaming: bool = Field(False, description="Enable streaming responses")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens for response")


class ChatEngineConfig(BaseModel):
    """Configuration for chat engine creation"""
    llm_config: LLMConfigRequest = Field(..., description="LLM configuration")
    user_id: Optional[str] = Field(None, description="User ID for document filtering")
    memory_type: MemoryType = Field(MemoryType.WINDOW, description="Memory type")
    max_history_length: int = Field(10, ge=1, le=50, description="Maximum conversation history length")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Generic success response model"""
    status: str = Field("success", description="Response status")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ConversationCreateRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID owning the conversation")
    title: Optional[str] = Field(None, description="Optional conversation title")


class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0
    is_pinned: Optional[bool] = False


class ConversationsListResponse(BaseModel):
    conversations: List[ConversationResponse]


class RenameConversationRequest(BaseModel):
    title: str


class DeleteConversationRequest(BaseModel):
    user_id: str = Field(..., description="User ID requesting the deletion")


class ChatMessageItem(BaseModel):
    id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ConversationMessagesResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessageItem]
    message_count: int
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
