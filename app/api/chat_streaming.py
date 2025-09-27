from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid
import os
from ..schemas.chat_schemas import ChatMessageRequest
from ..services.chat_service import get_chatbot_service
from ..services.chatbot.rag.query_preprocessing import preprocess_user_query
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat Streaming"])

@router.post("/stream")
async def stream_chat_message(request: ChatMessageRequest):
    """Stream chat responses with real-time token generation while preserving Knowledge Base functionality."""
    
    async def generate_stream():
        try:
            service = get_chatbot_service()
            if not service:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Chatbot service not initialized'})}\n\n"
                return

            # Preprocess the query for better retrieval (same as regular endpoint)
            preprocessed_query = preprocess_user_query(request.message)
            logger.info(f"STREAMING - Original query: {request.message}")
            logger.info(f"STREAMING - Preprocessed query: {preprocessed_query}")

            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Handle LLM configuration (same as regular endpoint)
            llm_config = request.llm_config or {}
            llm_config['streaming'] = True  # Enable streaming
            
            # Apply environment-based defaults if no config provided
            if not request.llm_config:
                provider = os.getenv('LLM_PROVIDER', 'groq').lower()
                llm_config = {
                    'provider': provider,
                    'model': os.getenv(f'{provider.upper()}_MODEL', 'llama-3.1-8b-instant'),
                    'temperature': 0.7,
                    'streaming': True
                }

            # Ensure API keys are available (same logic as regular endpoint)
            provider = llm_config.get('provider', 'groq').lower()
            if provider == 'groq' and not llm_config.get('api_key'):
                key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
                if key:
                    llm_config['api_key'] = key
                else:
                    yield f"data: {json.dumps({'type': 'error', 'data': 'GROQ_API_KEY not found'})}\n\n"
                    return
            elif provider == 'deepseek' and not llm_config.get('api_key'):
                key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
                if key:
                    llm_config['api_key'] = key
                else:
                    yield f"data: {json.dumps({'type': 'error', 'data': 'DEEPSEEK_API_KEY not found'})}\n\n"
                    return

            # Create chat engine with streaming support
            chat_engine = service.get_or_create_chat_engine(
                llm_config=llm_config,
                user_id=request.user_id,
                memory_type=request.memory_type.value
            )

            # Log Knowledge Base mode (same as regular endpoint)
            if request.selected_document_ids:
                logger.info(f"STREAMING: Knowledge Base mode with {len(request.selected_document_ids)} documents")
                logger.info(f"Selected document IDs: {request.selected_document_ids}")
            else:
                logger.info(f"STREAMING: Full database search mode")

            # Stream the response with all current functionality
            async for chunk in chat_engine.process_streaming_query(
                query=preprocessed_query,
                conversation_id=conversation_id,
                user_id=request.user_id,
                search_mode=request.search_mode.value,
                selected_document_ids=request.selected_document_ids
            ):
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )
