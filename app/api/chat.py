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
    ErrorResponse, SuccessResponse, LLMProvider, MemoryType, SearchMode,
    ConversationCreateRequest, ConversationResponse, ConversationsListResponse, RenameConversationRequest,
    DeleteConversationRequest
)
from ..services.chat_service import get_chatbot_service, initialize_chatbot_service
from app.services.chatbot.rag.chat_engine import LangChainChatEngine
from app.services.chatbot.title_generation.title_generator import ConversationTitleGenerator
from app.core.database import get_db
from app.db.conversations import get_conversations, get_messages
# JWT middleware not implemented yet
from ..services.chatbot.rag.conversation_summarizer import ConversationSummarizer
from ..services.chatbot.rag.query_preprocessing import preprocess_user_query
from ..core.config import settings
from uuid import UUID

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

def extract_document_sources_from_langchain(source_documents):
    """Extract document names directly from source documents returned by LangChain"""
    formatted_sources = []
    
    if not source_documents:
        logger.warning("No source documents provided")
        return formatted_sources
    
    logger.info(f"Processing {len(source_documents)} source documents")
    
    # Extract unique document IDs from source documents
    used_doc_ids = set()
    for source_doc in source_documents:
        # Handle both LangChain Document objects and dict objects
        if hasattr(source_doc, 'metadata'):
            metadata = source_doc.metadata
        else:
            metadata = source_doc.get('metadata', {})
            
        doc_id = metadata.get('document_id')
        filename = metadata.get('filename', '')
        
        if doc_id:
            used_doc_ids.add(doc_id)
            logger.info(f"Found source document: {doc_id} ({filename})")
    
    if not used_doc_ids:
        logger.warning("No document IDs found in source documents")
        return formatted_sources
    
    # Use filename from metadata directly instead of database lookup
    for doc_id in used_doc_ids:
        # Find the original source document to get filename
        filename = None
        for source_doc in source_documents:
            if hasattr(source_doc, 'metadata'):
                metadata = source_doc.metadata
            else:
                metadata = source_doc.get('metadata', {})
            
            if metadata.get('document_id') == doc_id:
                filename = metadata.get('filename', f"Document {str(doc_id)[:8]}...")
                break
        
        if filename:
            formatted_sources.append({
                'title': filename,
                'type': 'document'
            })
    
    logger.info(f"Successfully processed {len(formatted_sources)} document sources")
    return formatted_sources

def extract_sources_from_structured_result(result):
    """Extract sources from universal citation result with quotes."""
    if 'sources' in result and result['sources']:
        # Use the actual sources identified by the LLM through universal citations
        # These already contain quotes from the UniversalCitationChain
        return result['sources']
    else:
        # Fallback to source documents if no structured sources
        source_documents = result.get('source_documents', [])
        return extract_document_sources_from_langchain(source_documents)

def display_sources_in_terminal(sources):
    """Display sources in terminal - works with ANY source format."""
    if not sources:
        print("\n🔍 No sources found")
        return
        
    print("\n" + "=" * 80)
    print("📚 SOURCES USED:")
    print("=" * 80)
    
    for i, source in enumerate(sources, 1):
        # Handle different source formats
        if isinstance(source, str):
            filename = source
            quote = "Source document referenced"
        elif isinstance(source, dict):
            filename = source.get('title', source.get('filename', 'Unknown Document'))
            quote = source.get('quote', 'Referenced by AI')
        else:
            filename = str(source)
            quote = "Source referenced"
        
        print(f"\n📄 SOURCE {i}: {filename}")
        print(f"📝 TEXT USED:")
        print(f'   "{quote}"')
        print("-" * 60)
    
    print("=" * 80 + "\n")

# Initialize chat service on module load
def initialize_chat_service():
    """Initialize the chat service with configuration"""
    try:
        config = {
            'vector_db_path': os.path.abspath(getattr(settings, 'VECTOR_DB_PATH', './chroma_db')),
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


@router.post("/send", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a chat message and get AI response
    
    This endpoint processes user messages and returns AI responses based on
    indexed documents and conversation history.
    """
    try:
        # Validate conversation ID format if provided
        if request.conversation_id:
            # Allow test_conv_id for testing, but validate all other IDs as UUIDs
            if request.conversation_id != "test_conv_id":
                try:
                    UUID(request.conversation_id)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="Invalid conversation ID format. Must be a valid UUID.")
        
        # Get or create conversation
        conversation_repo = get_conversations()
        message_repo = get_messages()
        
        conversation_id = request.conversation_id
        if not conversation_id or conversation_id == "test_conv_id":
            # Create new conversation if none provided
            conv = conversation_repo.create(
                user_id=UUID(request.user_id) if request.user_id else None,
                title=None
            )
            conversation_id = str(conv.id) if conv else str(uuid.uuid4())
        else:
            # Verify conversation exists
            conv = conversation_repo.get(UUID(conversation_id))
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Preprocess user query for better retrieval
        preprocessed_query = preprocess_user_query(request.message)
        logger.info(f"Query preprocessing: '{request.message}' -> '{preprocessed_query}'")
        
        # Store user message in database (store original message, not preprocessed)
        user_message = message_repo.add(
            conversation_id=UUID(conversation_id),
            role="user",
            content=request.message,
            metadata={
                "user_id": request.user_id,
                "memory_type": request.memory_type.value,
                "preprocessed_query": preprocessed_query
            }
        )
        
        # Check if summarization is needed
        messages = message_repo.list(UUID(conversation_id))
        user_count = len([m for m in messages if m.role == "user"])
        assistant_count = len([m for m in messages if m.role == "assistant"])
        message_pairs = min(user_count, assistant_count)
        
        
        # Trigger summarization if needed (16+ message pairs or high token usage)
        estimated_tokens = sum(len(m.content) // 4 for m in messages)
        context_window_usage = estimated_tokens / 32000  # Assuming 32k context window
        needs_summarization = message_pairs >= 16 or context_window_usage >= 0.7
        
        if needs_summarization:
            logger.info(f"Summarization triggered for conversation {conversation_id}: {message_pairs} pairs, {context_window_usage:.2%} context usage")
            try:
                # Build messages payload for summarization
                convo_msgs = [
                    {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                    for m in messages
                ]
                summarizer = ConversationSummarizer()
                summary_text = summarizer.create_conversation_summary(convo_msgs)

                # Store summary as a system message
                message_repo.add(
                    conversation_id=UUID(conversation_id),
                    role="system",
                    content=f"Previous conversation summary: {summary_text}",
                    metadata={"type": "conversation_summary", "original_length": len(messages)}
                )

                # Prune older messages, keep last 8 pairs (plus summary we just added)
                deleted = message_repo.prune_keep_last_pairs(UUID(conversation_id), keep_pairs=8)
                logger.info(f"Pruned {deleted} old messages for conversation {conversation_id}")
            except Exception as se:
                logger.warning(f"Summarization/pruning failed for conversation {conversation_id}: {se}")
        
        # Generate actual AI response using chatbot service, with on-demand init and provider fallback
        ai_response = None
        try:
            try:
                service = get_chatbot_service()
            except RuntimeError:
                initialize_chat_service()
                service = get_chatbot_service()

            # Base LLM config - use provider from environment
            default_provider = getattr(settings, 'LLM_PROVIDER', 'groq').lower()
            
            if default_provider == 'groq':
                default_config = {
                    'provider': 'groq',
                    'api_key': getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY'),
                    'model': getattr(settings, 'DEFAULT_LLM_MODEL', 'llama-3.1-8b-instant'),
                    'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                    'streaming': False
                }
            elif default_provider == 'deepseek':
                default_config = {
                    'provider': 'deepseek',
                    'api_key': getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY'),
                    'model': getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat'),
                    'temperature': getattr(settings, 'DEEPSEEK_TEMPERATURE', 0.7),
                    'streaming': False
                }
            elif default_provider == 'openai':
                default_config = {
                    'provider': 'openai',
                    'api_key': getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY'),
                    'model': 'gpt-3.5-turbo',
                    'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                    'streaming': False
                }
            elif default_provider == 'gemini':
                default_config = {
                    'provider': 'gemini',
                    'api_key': getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY'),
                    'model': 'gemini-1.5-flash',
                    'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                    'streaming': False
                }
            else:
                # Fallback to groq if unknown provider
                default_config = {
                    'provider': 'groq',
                    'api_key': getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY'),
                    'model': 'llama-3.1-8b-instant',
                    'temperature': 0.7,
                    'streaming': False
                }
            
            llm_config = request.llm_config or default_config

            def ensure_api_key(conf: Dict[str, Any]) -> None:
                provider = conf.get('provider')
                if provider == 'groq' and not conf.get('api_key'):
                    key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
                    if key:
                        conf['api_key'] = key
                    else:
                        raise HTTPException(status_code=400, detail='GROQ_API_KEY not found in environment variables')
                elif provider == 'gemini' and not conf.get('api_key'):
                    key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
                    if key:
                        conf['api_key'] = key
                    else:
                        raise HTTPException(status_code=400, detail='GEMINI_API_KEY not found in environment variables')
                elif provider == 'openai' and not conf.get('api_key'):
                    key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
                    if key:
                        conf['api_key'] = key
                    else:
                        raise HTTPException(status_code=400, detail='OPENAI_API_KEY not found in environment variables')
                elif provider == 'deepseek' and not conf.get('api_key'):
                    key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
                    if key:
                        conf['api_key'] = key
                    else:
                        raise HTTPException(status_code=400, detail='DEEPSEEK_API_KEY not found in environment variables')

            def build_engine(conf: Dict[str, Any]):
                ensure_api_key(conf)
                return service.get_or_create_chat_engine(
                    llm_config=conf,
                    user_id=request.user_id,
                    memory_type=request.memory_type.value
                )

            # Try primary provider
            try:
                chat_engine = build_engine(dict(llm_config))
                result = await chat_engine.process_query(
                    query=preprocessed_query,  # Use preprocessed query for better retrieval
                    conversation_id=conversation_id,
                    user_id=request.user_id,
                    search_mode=request.search_mode.value,
                    selected_document_ids=request.selected_document_ids
                )
                ai_response = result['response']
                sources_data = result.get('sources', [])
            except Exception as primary_err:
                logger.error(f"Primary provider ({llm_config.get('provider')}) failed: {primary_err}")
                # Don't fallback - raise the original error so user knows what's wrong
                raise HTTPException(status_code=500, detail=f"LLM provider '{llm_config.get('provider')}' failed: {str(primary_err)}")

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to generate AI response, falling back to mock after retries")
            ai_response = f"I apologize, but I'm currently unable to process your request due to a technical issue. Please try again later. Your message was: {request.message}"
            sources_data = []
        
        # Extract and format sources using the new structured citation method
        formatted_sources = []
        if 'result' in locals() and result:
            # Use the new structured source extraction method
            formatted_sources = extract_sources_from_structured_result(result)
            
            # Display sources in terminal (bulletproof method)
            display_sources_in_terminal(formatted_sources)
            
            # Log the sources for debugging
            if formatted_sources:
                source_names = [s.get('title', 'Unknown') for s in formatted_sources]
                logger.info(f"Final sources to display: {source_names}")
                
                # Count sources with quotes for additional logging
                quoted_sources = [s for s in formatted_sources if s.get('quote')]
                if quoted_sources:
                    logger.info(f"Sources with exact quotes: {len(quoted_sources)} out of {len(formatted_sources)}")
                    logger.info(f"Saving quotes to database for conversation {conversation_id}")
            else:
                logger.warning("No sources extracted from result")
        
        # Store assistant message in database with sources (including quotes)
        assistant_message = message_repo.add(
            conversation_id=UUID(conversation_id),
            role="assistant", 
            content=ai_response,
            metadata={
                "processing_time": 0.1,
                "needs_summarization": needs_summarization,
                "message_pairs": message_pairs,
                "context_window_usage": context_window_usage,
                "sources": formatted_sources  # Store sources in metadata (now includes quotes)
            }
        )
        
        # Title generation is now handled by database trigger
        # No application-level title generation needed
        
        # Prepare response
        return ChatMessageResponse(
            response=ai_response,
            conversation_id=conversation_id,
            sources=formatted_sources,
            metadata={
                "processing_time": 0.1,
                "user_id": request.user_id,
                "memory_type": request.memory_type.value,
                "search_mode": request.search_mode.value,
                "needs_summarization": needs_summarization,
                "message_pairs": message_pairs,
                "context_window_usage": context_window_usage
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Compatibility alias: many tests/tools call /api/chat/message
@router.post("/message", response_model=ChatMessageResponse)
async def send_message_alias(request: ChatMessageRequest):
    """
    Compatibility alias for clients that post to /api/chat/message.
    Forwards to the same handler as /api/chat/send.
    """
    return await send_message(request)
        



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
        
        # Prepare LLM config with streaming enabled - use provider from environment
        default_provider = getattr(settings, 'LLM_PROVIDER', 'groq').lower()
        
        if default_provider == 'groq':
            default_streaming_config = {
                'provider': 'groq',
                'api_key': getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY'),
                'model': getattr(settings, 'DEFAULT_LLM_MODEL', 'llama-3.1-8b-instant'),
                'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                'streaming': True
            }
        elif default_provider == 'deepseek':
            default_streaming_config = {
                'provider': 'deepseek',
                'api_key': getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY'),
                'model': getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat'),
                'temperature': getattr(settings, 'DEEPSEEK_TEMPERATURE', 0.7),
                'streaming': True
            }
        elif default_provider == 'openai':
            default_streaming_config = {
                'provider': 'openai',
                'api_key': getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-3.5-turbo',
                'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                'streaming': True
            }
        elif default_provider == 'gemini':
            default_streaming_config = {
                'provider': 'gemini',
                'api_key': getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY'),
                'model': 'gemini-1.5-flash',
                'temperature': getattr(settings, 'DEFAULT_TEMPERATURE', 0.7),
                'streaming': True
            }
        else:
            # Fallback to groq
            default_streaming_config = {
                'provider': 'groq',
                'api_key': os.getenv('GROQ_API_KEY'),
                'model': 'llama-3.1-8b-instant',
                'temperature': 0.7,
                'streaming': True
            }
        
        llm_config = request.llm_config or default_streaming_config
        
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
        elif llm_config.get('provider') == 'deepseek' and not llm_config.get('api_key'):
            deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or os.getenv('DEEPSEEK_API_KEY')
            if deepseek_key:
                llm_config['api_key'] = deepseek_key
            else:
                raise HTTPException(status_code=400, detail="DEEPSEEK_API_KEY not found in environment variables")
        
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
        
        # Preprocess search query for better retrieval
        preprocessed_query = preprocess_user_query(request.query)
        logger.debug(f"Search query preprocessing: '{request.query}' -> '{preprocessed_query}'")
        
        # Search documents
        results = service.search_documents(
            query=preprocessed_query,
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

@router.get("/conversations/{conversation_id}/context")
async def get_conversation_context(conversation_id: str, include_summary: bool = True):
    """
    Get conversation context including history and statistics
    """
    try:
        # Return a simple response without database calls for now
        # This will prevent the hanging issue
        context = {
            "conversation_id": conversation_id,
            "total_messages": 0,
            "stats": {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "message_pairs": 0,
                "estimated_tokens": 0,
                "needs_summarization": False,
                "summarization_enabled": True
            },
            "recent_messages": []
        }
        
        return context
            
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conversation_id}/summarize")
async def force_conversation_summarization(conversation_id: str):
    """
    Manually trigger conversation summarization
    """
    try:
        # For now, return a placeholder response
        # You'll need to implement the actual summarization logic
        return {
            "optimized_messages": [],
            "summary": "Summarization endpoint implemented but logic needs to be connected"
        }
    except Exception as e:
        logger.error(f"Error in conversation summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/stats")
async def get_conversation_stats(conversation_id: str):
    """
    Get conversation statistics
    """
    try:
        conversation_repo = get_conversations()
        message_repo = get_messages()
        
        conv = conversation_repo.get(UUID(conversation_id))
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        msgs = message_repo.list(UUID(conversation_id))
        
        user_messages = len([m for m in msgs if m.role == "user"])
        assistant_messages = len([m for m in msgs if m.role == "assistant"])
        message_pairs = min(user_messages, assistant_messages)
        estimated_tokens = sum(len(m.content) // 4 for m in msgs)
        context_window_usage = estimated_tokens / 32000
        
        stats = {
            "total_messages": len(msgs),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "message_pairs": message_pairs,
            "estimated_tokens": estimated_tokens,
            "needs_summarization": message_pairs >= 16 or context_window_usage >= 0.7,
            "summarization_enabled": True,
            "context_window_usage": context_window_usage
        }
        
        return stats
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str, format_type: str = "json"):
    """
    Export conversation data
    """
    try:
        conversation_repo = get_conversations()
        message_repo = get_messages()
        
        try:
            conv = conversation_repo.get(UUID(conversation_id))
            msgs = message_repo.list(UUID(conversation_id))
            
            if format_type == "text":
                # Format as text
                formatted_messages = []
                for msg in msgs:
                    role_name = "Human" if msg.role == "user" else "Assistant"
                    formatted_messages.append(f"{role_name}: {msg.content}")
                return "\n".join(formatted_messages)
            else:
                # Return as JSON
                return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in msgs]
                
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
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
async def delete_conversation(conversation_id: str, request: DeleteConversationRequest):
    """
    Delete a conversation and all its messages
    
    This endpoint removes a conversation and all associated messages
    for the authenticated user.
    """
    try:
        conversation_repo = get_conversations()
        message_repo = get_messages()
        
        # Verify conversation exists and belongs to the user
        conv = conversation_repo.get(UUID(conversation_id))
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if the conversation belongs to the requesting user
        if conv.user_id and str(conv.user_id) != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only delete your own conversations")
        
        # Delete all messages in the conversation first
        message_repo.delete_by_conversation(UUID(conversation_id))
        
        # Delete the conversation
        conversation_repo.delete(UUID(conversation_id))
        
        return SuccessResponse(message=f"Conversation {conversation_id} deleted successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
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
        
        # Use the optimized query that filters empty conversations
        conversations = conversation_repo.list_with_message_counts(UUID(user_id), limit, offset)
        
        # Convert to proper format
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                "id": str(conv["id"]),
                "user_id": str(conv["user_id"]) if conv["user_id"] else None,
                "title": conv["title"],
                "created_at": conv["created_at"].isoformat() if conv["created_at"] else None,
                "updated_at": conv["updated_at"].isoformat() if conv["updated_at"] else None,
                "message_count": conv["message_count"]
            })
        
        return {"conversations": formatted_conversations}
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
    Health check endpoint for the chat service
    """
    try:
        service = get_chatbot_service()
        stats = service.get_system_stats()
        return {"status": "healthy", "stats": stats}
        
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


@router.post("/clear-cache")
async def clear_chat_cache():
    """
    Clear the chat engine cache to force recreation of LLM instances.
    
    This is useful when switching providers or updating configurations.
    """
    try:
        service = get_chatbot_service()
        service.clear_cache()
        return {"status": "success", "message": "Chat engine cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
