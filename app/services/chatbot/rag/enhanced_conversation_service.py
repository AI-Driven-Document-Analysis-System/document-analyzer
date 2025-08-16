from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import uuid
from .conversation_manager import ConversationManager
from .conversation_summarizer import ConversationSummarizer
from .chat_engine import LangChainChatEngine
from ..chains.conversational_chain import CustomConversationalChain

logger = logging.getLogger(__name__)


class EnhancedConversationService:
    """
    Enhanced conversation service that integrates conversation management,
    summarization, and chat functionality with smart context preservation.
    
    This service provides:
    - Intelligent conversation summarization to prevent context loss
    - Automatic context optimization when approaching token limits
    - Preservation of key insights and findings across long conversations
    - Unified interface for conversation management and chat processing
    """
    
    def __init__(self, conversational_chain: CustomConversationalChain, 
                 enable_summarization: bool = True, 
                 max_history_length: int = 10):
        """
        Initialize the enhanced conversation service.
        
        Args:
            conversational_chain (CustomConversationalChain): The conversational chain for processing
            enable_summarization (bool): Whether to enable conversation summarization
            max_history_length (int): Maximum number of message pairs to keep in detailed history
        """
        self.conversational_chain = conversational_chain
        self.conversation_manager = ConversationManager(
            max_history_length=max_history_length,
            enable_summarization=enable_summarization
        )
        self.summarizer = ConversationSummarizer() if enable_summarization else None
        
        # Configuration
        self.max_detailed_messages = 8
        self.summarization_threshold = 16
        
    async def process_message(self, conversation_id: str, user_message: str, 
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response with smart context management.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            user_message (str): The user's message
            user_id (Optional[str]): User identifier for tracking
            
        Returns:
            Dict[str, Any]: Response containing answer, sources, and conversation info
        """
        try:
            # Add user message to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role='user',
                content=user_message,
                metadata={'user_id': user_id, 'timestamp': datetime.now().isoformat()}
            )
            
            # Get conversation history for context
            conversation_history = self.conversation_manager.get_conversation_history(
                conversation_id, format_for_llm=True
            )
            
            # Process the query through the conversational chain
            result = await self.conversational_chain.arun(
                question=user_message,
                callbacks=None
            )
            
            # Add assistant response to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role='assistant',
                content=result["answer"],
                metadata={'timestamp': datetime.now().isoformat()}
            )
            
            # Check if summarization is needed after adding the response
            conversation_stats = self.conversation_manager.get_conversation_stats(conversation_id)
            
            # Extract and format source documents
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    'content': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    'metadata': doc.metadata,
                    'score': doc.metadata.get('score', 0)
                })
            
            # Prepare response
            response = {
                'conversation_id': conversation_id,
                'response': result["answer"],
                'sources': sources,
                'chat_history': self.conversation_manager.get_conversation_history(conversation_id),
                'conversation_stats': conversation_stats,
                'context_optimized': conversation_stats.get('needs_summarization', False)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise Exception(f"Error processing message: {str(e)}")
    
    def get_conversation_context(self, conversation_id: str, 
                               include_summary: bool = True) -> Dict[str, Any]:
        """
        Get the current conversation context including history and statistics.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            include_summary (bool): Whether to include conversation summary
            
        Returns:
            Dict[str, Any]: Conversation context information
        """
        if conversation_id not in self.conversation_manager.conversations:
            return {}
            
        messages = self.conversation_manager.conversations[conversation_id]
        stats = self.conversation_manager.get_conversation_stats(conversation_id)
        
        context = {
            'conversation_id': conversation_id,
            'total_messages': len(messages),
            'stats': stats,
            'recent_messages': messages[-10:] if len(messages) > 10 else messages
        }
        
        if include_summary and self.summarizer:
            # Check if there's already a summary in the conversation
            summary_messages = [msg for msg in messages 
                              if msg.get('role') == 'system' and 
                              msg.get('metadata', {}).get('type') == 'conversation_summary']
            
            if summary_messages:
                context['existing_summary'] = summary_messages[-1]['content']
            else:
                context['summary_available'] = stats.get('needs_summarization', False)
        
        return context
    
    def optimize_conversation_context(self, conversation_id: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Manually trigger conversation context optimization.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            
        Returns:
            Tuple[List[Dict], str]: Optimized messages and summary
        """
        if not self.summarizer:
            return self.conversation_manager.conversations.get(conversation_id, []), ""
            
        return self.conversation_manager.force_summarization(conversation_id)
    
    def create_new_conversation(self, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            user_id (Optional[str]): User identifier for tracking
            
        Returns:
            str: New conversation ID
        """
        conversation_id = str(uuid.uuid4())
        
        # Initialize conversation with system message
        self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role='system',
            content='New conversation started. Ready to help with document analysis.',
            metadata={'user_id': user_id, 'type': 'conversation_start'}
        )
        
        return conversation_id
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """
        Get a summary of the conversation if available.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            
        Returns:
            Optional[str]: Conversation summary or None if not available
        """
        if not self.summarizer:
            return None
            
        messages = self.conversation_manager.conversations.get(conversation_id, [])
        if not messages:
            return None
            
        # Check if there's already a summary
        summary_messages = [msg for msg in messages 
                          if msg.get('role') == 'system' and 
                          msg.get('metadata', {}).get('type') == 'conversation_summary']
        
        if summary_messages:
            return summary_messages[-1]['content']
        
        # Generate new summary if needed
        if self.summarizer.should_summarize(len(messages) // 2):
            summary = self.summarizer.create_conversation_summary(messages)
            return summary
            
        return None
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get information about all active conversations.
        
        Returns:
            List[Dict[str, Any]]: List of conversation information
        """
        conversation_ids = self.conversation_manager.get_all_conversation_ids()
        conversations = []
        
        for conv_id in conversation_ids:
            conv_info = self.get_conversation_context(conv_id)
            conversations.append(conv_info)
            
        return conversations
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear a specific conversation.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            
        Returns:
            bool: True if conversation was cleared, False if not found
        """
        if conversation_id in self.conversation_manager.conversations:
            self.conversation_manager.clear_conversation(conversation_id)
            return True
        return False
    
    def export_conversation(self, conversation_id: str, 
                          format_type: str = 'json') -> str:
        """
        Export conversation data in specified format.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            format_type (str): Export format ('json' or 'text')
            
        Returns:
            str: Exported conversation data
        """
        if conversation_id not in self.conversation_manager.conversations:
            return ""
            
        if format_type == 'text':
            return self.conversation_manager.get_conversation_history(
                conversation_id, format_for_llm=True
            )
        else:
            return self.conversation_manager.get_conversation_history(
                conversation_id, format_for_llm=False
            ) 