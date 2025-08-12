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
    ErrorResponse, SuccessResponse, LLMProvider, MemoryType
)
from ..services.chat_service import get_chatbot_service, initialize_chatbot_service
from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize chat service on module load
def initialize_chat_service():
    """Initialize the chat service with configuration"""
    try:
        config = {
            'vector_db_path': getattr(settings, 'VECTOR_DB_PATH', './data/chroma_db'),
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
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Prepare LLM config (use default if not provided)
        llm_config = request.llm_config or {
            'provider': 'gemini',
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': 'gemini-1.5-flash',
            'temperature': 0.7,
            'streaming': False
        }
        
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
            results=results,
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
        service = get_chatbot_service()
        
        # Get conversation history
        history = service.get_conversation_history(conversation_id)
        
        # Parse history into messages (simplified for now)
        messages = []
        if history:
            # TODO: Parse conversation history properly
            messages = [{"role": "system", "content": history}]
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            message_count=len(messages),
            created_at=None,  # TODO: Track conversation timestamps
            last_updated=None
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
        service = get_chatbot_service()
        
        # Clear conversation
        service.clear_conversation(conversation_id)
        
        return SuccessResponse(
            message=f"Conversation {conversation_id} cleared successfully"
        )
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
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
