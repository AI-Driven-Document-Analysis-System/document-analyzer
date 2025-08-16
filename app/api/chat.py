from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import logging
import time
import uuid
from typing import Optional, Dict, Any
import os

from ..schemas.chat_schemas import (
    ChatMessageRequest, ChatMessageResponse, DocumentIndexRequest, DocumentIndexResponse,
    DocumentSearchRequest, DocumentSearchResponse, ConversationHistoryRequest, 
    ConversationHistoryResponse, SystemStatsResponse, LLMConfigRequest, ChatEngineConfig,
    ErrorResponse, SuccessResponse, LLMProvider, MemoryType,
    ConversationCreateRequest, ConversationResponse, ConversationsListResponse, RenameConversationRequest
)
from ..services.chat_service import get_chatbot_service, initialize_chatbot_service
from ..core.config import settings
from ..db.conversations import get_conversations, get_messages
from uuid import UUID

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize chat service on module load
def initialize_chat_service():
    """Initialize the chat service with configuration"""
    try:
        config = {
            'vector_db_path': getattr(settings, 'VECTOR_DB_PATH', './chroma_db'),
            'collection_name': getattr(settings, 'COLLECTION_NAME', 'documents'),
            'chunk_size': getattr(settings, 'CHUNK_SIZE', 1000),
            'chunk_overlap': getattr(settings, 'CHUNK_OVERLAP', 200),
            'embedding_model': getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
            'max_history_length': getattr(settings, 'MAX_HISTORY_LENGTH', 10)
        }
        
        initialize_chatbot_service(config)
        logger.info("Chat service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chat service: {e}")
        raise

# Initialize on import
try:
    initialize_chat_service()
except Exception as e:
    logger.warning(f"Chat service initialization deferred: {e}")


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a chat message and get AI response
    
    This endpoint processes user messages and returns AI responses based on
    indexed documents and conversation history.
    """
    try:
        service = get_chatbot_service()
        conversation_repo = get_conversations()
        message_repo = get_messages()
        
        # Ensure a conversation exists
        if request.conversation_id:
            conversation_id = request.conversation_id
        else:
            # Create a new conversation for this user
            conv = conversation_repo.create(user_id=UUID(request.user_id) if request.user_id else uuid.uuid4())
            conversation_id = str(conv.id) if conv else str(uuid.uuid4())
        
        # Prepare LLM config (use default if not provided)
        llm_config = request.llm_config or {
            'provider': 'gemini',
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': 'gemini-1.5-flash',
            'temperature': 0.7,
            'streaming': False
        }
        
        # Ensure API key is set based on provider
        if llm_config.get('provider') == 'groq' and not llm_config.get('api_key'):
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                llm_config['api_key'] = groq_key
            else:
                raise HTTPException(status_code=400, detail="GROQ_API_KEY not found in environment variables")
        elif llm_config.get('provider') == 'gemini' and not llm_config.get('api_key'):
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                llm_config['api_key'] = gemini_key
            else:
                raise HTTPException(status_code=400, detail="GEMINI_API_KEY not found in environment variables")
        elif llm_config.get('provider') == 'openai' and not llm_config.get('api_key'):
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                llm_config['api_key'] = openai_key
            else:
                raise HTTPException(status_code=400, detail="OPENAI_API_KEY not found in environment variables")
        
        # Validate API key is present
        if not llm_config.get('api_key'):
            raise HTTPException(status_code=400, detail=f"API key not found for provider: {llm_config.get('provider')}")
        
        # Get or create chat engine
        chat_engine = service.get_or_create_chat_engine(
            llm_config=llm_config,
            user_id=request.user_id,
            memory_type=request.memory_type.value
        )
        
        # Process the message
        start_time = time.time()
        
        # Try different methods to get response
        try:
            # Try the chat method first
            response = chat_engine.chat(request.message)
        except AttributeError:
            try:
                # Try the run method
                result = chat_engine.chain.run(request.message)
                response = result.get('answer', str(result)) if isinstance(result, dict) else str(result)
            except Exception as e:
                logger.error(f"Failed to get response from chat engine: {e}")
                raise HTTPException(status_code=500, detail="Failed to process chat message")
        
        processing_time = time.time() - start_time
        
        # Persist user message and assistant response
        try:
            conv_uuid = UUID(conversation_id)
        except Exception:
            conv_uuid = uuid.uuid4()
        try:
            message_repo.add(conv_uuid, role="user", content=request.message, metadata={"user_id": request.user_id})
            message_repo.add(conv_uuid, role="assistant", content=response, metadata={"llm_provider": llm_config.get('provider')})
        except Exception as e:
            logger.warning(f"Failed to persist chat messages: {e}")
        
        # Prepare response
        return ChatMessageResponse(
            response=response,
            conversation_id=conversation_id,
            sources=[],  # TODO: Extract sources from response
            metadata={
                "processing_time": processing_time,
                "user_id": request.user_id,
                "memory_type": request.memory_type.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/stream")
async def send_message_stream(request: ChatMessageRequest):
    """
    Send a chat message and get streaming AI response
    
    This endpoint provides real-time streaming responses for better user experience.
    """
    try:
        service = get_chatbot_service()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Prepare LLM config with streaming enabled
        llm_config = request.llm_config or {
            'provider': 'gemini',
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': 'gemini-1.5-flash',
            'temperature': 0.7,
            'streaming': True  # Enable streaming
        }
        
        # Ensure API key is set based on provider
        if llm_config.get('provider') == 'groq' and not llm_config.get('api_key'):
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                llm_config['api_key'] = groq_key
            else:
                raise HTTPException(status_code=400, detail="GROQ_API_KEY not found in environment variables")
        elif llm_config.get('provider') == 'gemini' and not llm_config.get('api_key'):
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                llm_config['api_key'] = gemini_key
            else:
                raise HTTPException(status_code=400, detail="GEMINI_API_KEY not found in environment variables")
        elif llm_config.get('provider') == 'openai' and not llm_config.get('api_key'):
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                llm_config['api_key'] = openai_key
            else:
                raise HTTPException(status_code=400, detail="OPENAI_API_KEY not found in environment variables")
        
        # Validate API key is present
        if not llm_config.get('api_key'):
            raise HTTPException(status_code=400, detail=f"API key not found for provider: {llm_config.get('provider')}")
        
        # Get or create chat engine
        chat_engine = service.get_or_create_chat_engine(
            llm_config=llm_config,
            user_id=request.user_id,
            memory_type=request.memory_type.value
        )
        
        # TODO: Implement streaming response
        # For now, return a simple streaming response
        async def generate_stream():
            yield f"data: {conversation_id}\n\n"
            yield f"data: {request.message}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        logger.error(f"Error processing streaming chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/index", response_model=DocumentIndexResponse)
async def index_document(request: DocumentIndexRequest):
    """
    Index a document for chat retrieval
    
    This endpoint processes and indexes documents so they can be used
    for context in chat conversations.
    """
    try:
        service = get_chatbot_service()
        
        # Prepare document data
        document_data = {
            'id': request.id,
            'text': request.text,
            'filename': request.filename,
            'user_id': request.user_id,
            **request.metadata
        }
        
        # Index the document
        chunk_ids = service.index_document(document_data)
        
        return DocumentIndexResponse(
            status="success",
            document_id=request.id,
            chunk_ids=chunk_ids,
            chunk_count=len(chunk_ids),
            message=f"Document indexed successfully with {len(chunk_ids)} chunks"
        )
        
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """
    Search for documents similar to the query
    
    This endpoint performs semantic search on indexed documents
    and returns relevant results.
    """
    try:
        service = get_chatbot_service()
        
        start_time = time.time()
        
        # Search documents
        results = service.search_documents(
            query=request.query,
            k=request.k,
            user_id=request.user_id
        )
        
        search_time = time.time() - start_time
        
        return DocumentSearchResponse(
            query=request.query,
            documents=results,
            total_results=len(results),
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history for a specific conversation
    
    This endpoint retrieves the full conversation history
    for a given conversation ID.
    """
    try:
        conversation_repo = get_conversations()
        message_repo = get_messages()
        conv = conversation_repo.get(UUID(conversation_id))
        msgs = message_repo.list(UUID(conversation_id))
        messages_payload = [{"id": str(m.id), "role": m.role, "content": m.content, "metadata": m.metadata, "timestamp": m.timestamp} for m in msgs]
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages_payload,
            message_count=len(messages_payload),
            created_at=conv.created_at if conv else None,
            last_updated=conv.updated_at if conv else None
        )
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear conversation history for a specific conversation
    
    This endpoint removes all conversation history for the given
    conversation ID.
    """
    try:
        conversation_repo = get_conversations()
        conversation_repo.delete(UUID(conversation_id))
        return SuccessResponse(message=f"Conversation {conversation_id} cleared successfully")
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation_api(payload: ConversationCreateRequest):
    try:
        conversation_repo = get_conversations()
        conv = conversation_repo.create(user_id=UUID(payload.user_id) if payload.user_id else None, title=payload.title)
        return ConversationResponse(id=str(conv.id), user_id=str(conv.user_id) if conv.user_id else None, title=conv.title, created_at=conv.created_at, updated_at=conv.updated_at)
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=ConversationsListResponse)
async def list_conversations_api(user_id: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        conversation_repo = get_conversations()
        rows = conversation_repo.list(UUID(user_id), limit, offset)
        return {"conversations": [{"id": str(r.id), "user_id": str(r.user_id) if r.user_id else None, "title": r.title, "created_at": r.created_at, "updated_at": r.updated_at} for r in rows]}
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation_api(conversation_id: str, payload: RenameConversationRequest):
    try:
        conversation_repo = get_conversations()
        conv = conversation_repo.rename(UUID(conversation_id), payload.title)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationResponse(id=str(conv.id), user_id=str(conv.user_id) if conv.user_id else None, title=conv.title, created_at=conv.created_at, updated_at=conv.updated_at)
    except Exception as e:
        logger.error(f"Error renaming conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from the vector database
    
    This endpoint removes a document and all its associated chunks
    from the vector database.
    """
    try:
        service = get_chatbot_service()
        
        # Delete document
        service.delete_document(document_id)
        
        return SuccessResponse(
            message=f"Document {document_id} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """
    Get system statistics and health information
    
    This endpoint provides information about the chat service
    status, configuration, and performance metrics.
    """
    try:
        service = get_chatbot_service()
        
        # Get system stats
        stats = service.get_system_stats()
        
        return SystemStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/engine/create")
async def create_chat_engine(config: ChatEngineConfig):
    """
    Create a new chat engine with specific configuration
    
    This endpoint creates a new chat engine instance with
    custom LLM configuration and settings.
    """
    try:
        service = get_chatbot_service()
        
        # Convert LLM config to dict
        llm_config = {
            'provider': config.llm_config.provider.value,
            'api_key': config.llm_config.api_key,
            'model': config.llm_config.model,
            'temperature': config.llm_config.temperature,
            'streaming': config.llm_config.streaming
        }
        
        if config.llm_config.max_tokens:
            llm_config['max_tokens'] = config.llm_config.max_tokens
        
        # Create chat engine
        chat_engine = service.get_or_create_chat_engine(
            llm_config=llm_config,
            user_id=config.user_id,
            memory_type=config.memory_type.value
        )
        
        return SuccessResponse(
            message="Chat engine created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating chat engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for chat service
    
    This endpoint verifies that the chat service is running
    and properly initialized.
    """
    try:
        service = get_chatbot_service()
        stats = service.get_system_stats()
        
        return {
            "status": "healthy" if stats.get('initialized', False) else "unhealthy",
            "service": "chat",
            "initialized": stats.get('initialized', False),
            "timestamp": stats.get('timestamp')
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/db/health")
async def database_health_check():
    """
    Database health check endpoint
    
    This endpoint verifies database connectivity and connection pool status.
    """
    try:
        from ..core.database import db_manager
        
        # Check if pool is initialized
        if not db_manager.is_initialized():
            return {
                "status": "unhealthy",
                "database": "postgresql",
                "error": "Connection pool not initialized",
                "details": "Check DATABASE_URL environment variable",
                "timestamp": time.time()
            }
        
        # Test connection
        connection_test = db_manager.test_connection()
        pool_status = db_manager.get_pool_status()
        
        # Check environment variables
        env_info = {
            "DATABASE_URL_set": bool(os.getenv("DATABASE_URL")),
            "DATABASE_URL_length": len(os.getenv("DATABASE_URL", "")) if os.getenv("DATABASE_URL") else 0
        }
        
        return {
            "status": "healthy" if connection_test else "unhealthy",
            "database": "postgresql",
            "connection_test": connection_test,
            "pool_status": pool_status,
            "environment": env_info,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "database": "postgresql",
            "error": str(e),
            "timestamp": time.time()
        }


@router.post("/db/reconnect")
async def force_database_reconnect():
    """
    Force database reconnection
    
    This endpoint forces the database connection pool to reinitialize.
    Use only when experiencing connection issues.
    """
    try:
        from ..core.database import db_manager
        
        # Try to initialize the pool
        success = db_manager.initialize_pool()
        
        if success:
            # Test the new connection
            connection_test = db_manager.test_connection()
            return {
                "status": "success" if connection_test else "partial",
                "message": "Database connection pool reinitialized",
                "connection_test": connection_test,
                "timestamp": time.time()
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to reinitialize connection pool",
                "error": "Check DATABASE_URL and database connectivity",
                "timestamp": time.time()
            }
        
    except Exception as e:
        logger.error(f"Database reconnection failed: {e}")
        return {
            "status": "error",
            "message": "Database reconnection failed",
            "error": str(e),
            "timestamp": time.time()
        }
