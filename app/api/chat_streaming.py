from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid
import os
import time
import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation', 'rag-chatbot'))
# from quick_integration import capture_chatbot_interaction, init_evaluation_capture
from ..schemas.chat_schemas import ChatMessageRequest
from ..services.chat_service import get_chatbot_service
from ..services.chatbot.rag.query_preprocessing import preprocess_user_query
from ..core.config import settings
from ..db.conversations import get_conversations, get_messages
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat Streaming"])

# Initialize evaluation capture once (only if enabled)
try:
    from quick_integration import is_ragas_enabled
    if is_ragas_enabled():
        init_evaluation_capture()
        logger.info("RAGAS evaluation capture initialized")
    else:
        logger.info("RAGAS evaluation is disabled")
except Exception as e:
    logger.error(f"Failed to initialize evaluation capture: {e}")

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
            start_time = time.time()  # Track response time for evaluation
            
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
            collected_chunks = []
            async for chunk in chat_engine.process_streaming_query(
                query=preprocessed_query,
                conversation_id=conversation_id,
                user_id=request.user_id,
                search_mode=request.search_mode.value,
                selected_document_ids=request.selected_document_ids
            ):
                collected_chunks.append(chunk)
                yield f"data: {json.dumps(chunk)}\n\n"
            
            # Save messages to database for conversation history and title generation
            try:
                response_text = ''.join([c.get('data', '') for c in collected_chunks if c.get('type') == 'token'])
                
                # Ensure conversation exists - insert directly with the conversation_id from frontend
                conversations_repo = get_conversations()
                existing_conv = conversations_repo.get(UUID(conversation_id))
                if not existing_conv:
                    # Create conversation with specific ID
                    from datetime import datetime, timezone
                    now = datetime.now(timezone.utc)
                    query = """
                        INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """
                    conversations_repo.db.execute_query(
                        query, 
                        (UUID(conversation_id), UUID(request.user_id) if request.user_id else None, "New Chat", now, now)
                    )
                    logger.info(f"Created conversation {conversation_id}")
                
                # Save user message
                messages_repo = get_messages()
                messages_repo.add(
                    conversation_id=UUID(conversation_id),
                    role='user',
                    content=request.message,
                    metadata={}
                )
                
                # Extract sources from collected chunks
                sources = next((c.get('data', []) for c in collected_chunks if c.get('type') == 'sources'), [])
                logger.info(f"Extracted {len(sources)} sources from streaming chunks for conversation {conversation_id}")
                
                # Save assistant message with sources in metadata
                messages_repo.add(
                    conversation_id=UUID(conversation_id),
                    role='assistant',
                    content=response_text,
                    metadata={'sources': sources}
                )
                
                logger.info(f"Saved messages with {len(sources)} sources to conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Failed to save messages: {e}")
            
            # Capture interaction for RAGAS evaluation after streaming completes (if enabled)
            try:
                if is_ragas_enabled():
                    # Reconstruct the complete response from chunks
                    sources = next((c.get('data', []) for c in collected_chunks if c.get('type') == 'sources'), [])
                    retrieved_docs = next((c.get('data', []) for c in collected_chunks if c.get('type') == 'retrieved_docs'), [])
                    
                    chat_result = {
                        'response': response_text,
                        'sources': retrieved_docs,  # Use actual retrieved docs from vector DB
                        'conversation_id': conversation_id
                    }
                    
                    capture_result = capture_chatbot_interaction(
                        question=preprocessed_query,
                        chat_result=chat_result,
                        conversation_id=conversation_id,
                        start_time=start_time
                    )
                    
                    if capture_result:
                        logger.info(f"Captured interaction for evaluation: {preprocessed_query[:50]}... with {len(retrieved_docs)} retrieved docs")
            except Exception as e:
                logger.error(f"Failed to capture interaction: {e}")

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
