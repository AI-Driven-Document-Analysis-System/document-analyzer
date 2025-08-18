from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import json
from ..llm.llm_factory import LLMFactory
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Handles conversation summarization to prevent context loss when approaching token limits.
    
    This service implements a smart summarization strategy that:
    - Keeps the last 8 message exchanges in full detail
    - Summarizes older conversation parts when approaching token limits
    - Preserves key document findings, user preferences, and analysis results
    - Triggers summarization at 16 message pairs or 70% context window usage
    """
    
    def __init__(self, llm_provider: str = None, llm_model: str = None):
        """
        Initialize the conversation summarizer.
        
        Args:
            llm_provider (str): LLM provider to use for summarization
            llm_model (str): Specific model to use for summarization
        """
        self.llm_provider = llm_provider or settings.DEFAULT_LLM_PROVIDER
        self.llm_model = llm_model or settings.DEFAULT_LLM_MODEL
        self.llm = None
        self._initialize_llm()
        
        # Configuration for summarization strategy
        self.max_detailed_messages = 8  # Keep last 8 message exchanges in full detail
        self.summarization_threshold = 16  # Trigger summarization at 16 message pairs
        self.context_window_threshold = 0.7  # Trigger at 70% context window usage
        
        # Summarization prompt template
        self.summarization_prompt = """You are tasked with summarizing a conversation while preserving critical information. 

Please create a concise summary that captures:
1. Key document findings and insights discussed
2. User preferences and analysis requirements
3. Important decisions or conclusions reached
4. Context that would be valuable for continuing the conversation

Focus on preserving information that would be most useful for future conversation turns.

Conversation to summarize:
{conversation_text}

Please provide a clear, structured summary that maintains the essential context:"""

    def _initialize_llm(self):
        """Initialize the LLM for summarization."""
        try:
            if self.llm_provider == "openai":
                self.llm = LLMFactory.create_openai_llm(
                    api_key=settings.OPENAI_API_KEY,
                    model=self.llm_model,
                    temperature=0.3,  # Lower temperature for more consistent summarization
                    streaming=False
                )
            elif self.llm_provider == "gemini":
                self.llm = LLMFactory.create_gemini_llm(
                    api_key=settings.GEMINI_API_KEY,
                    model=self.llm_model,
                    temperature=0.3,
                    streaming=False
                )
            elif self.llm_provider == "groq":
                self.llm = LLMFactory.create_groq_llm(
                    api_key=settings.GROQ_API_KEY,
                    model=self.llm_model,
                    temperature=0.3,
                    streaming=False
                )
            else:
                # Fallback to Groq if no specific provider is configured
                self.llm = LLMFactory.create_groq_llm(
                    api_key=settings.GROQ_API_KEY,
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                    streaming=False
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM for summarization: {e}")
            self.llm = None

    def should_summarize(self, conversation_length: int, estimated_tokens: int = None) -> bool:
        """
        Determine if conversation should be summarized.
        
        Args:
            conversation_length (int): Number of message pairs in conversation
            estimated_tokens (int): Estimated token count (optional)
            
        Returns:
            bool: True if summarization should be triggered
        """
        # Trigger based on message count
        if conversation_length >= self.summarization_threshold:
            return True
            
        # Trigger based on estimated token usage (if available)
        if estimated_tokens:
            # Assuming a typical context window of 32k tokens
            context_window = 32000
            if estimated_tokens / context_window >= self.context_window_threshold:
                return True
                
        return False

    def create_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Create a summary of the conversation using the LLM.
        
        Args:
            messages (List[Dict]): List of conversation messages
            
        Returns:
            str: Generated summary of the conversation
        """
        if not self.llm:
            logger.warning("LLM not available for summarization, using fallback method")
            return self._fallback_summarization(messages)
            
        try:
            # Format conversation for summarization
            conversation_text = self._format_conversation_for_summarization(messages)
            
            # Generate summary using LLM
            if hasattr(self.llm, 'ainvoke'):
                # Async LLM - we'll handle this in the async version
                # For sync version, fall back to sync invoke
                result = self.llm.invoke(
                    self.summarization_prompt.format(conversation_text=conversation_text)
                )
                summary = result.content if hasattr(result, 'content') else str(result)
            else:
                # Sync LLM
                result = self.llm.invoke(
                    self.summarization_prompt.format(conversation_text=conversation_text)
                )
                summary = result.content if hasattr(result, 'content') else str(result)
                
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return self._fallback_summarization(messages)

    async def create_conversation_summary_async(self, messages: List[Dict[str, Any]]) -> str:
        """
        Async version of create_conversation_summary for async contexts.
        
        Args:
            messages (List[Dict]): List of conversation messages
            
        Returns:
            str: Generated summary of the conversation
        """
        if not self.llm:
            logger.warning("LLM not available for summarization, using fallback method")
            return self._fallback_summarization(messages)
            
        try:
            # Format conversation for summarization
            conversation_text = self._format_conversation_for_summarization(messages)
            
            # Generate summary using LLM
            if hasattr(self.llm, 'ainvoke'):
                # Async LLM
                result = await self.llm.ainvoke(
                    self.summarization_prompt.format(conversation_text=conversation_text)
                )
                summary = result.content if hasattr(result, 'content') else str(result)
            else:
                # Sync LLM - fall back to sync invoke
                result = self.llm.invoke(
                    self.summarization_prompt.format(conversation_text=conversation_text)
                )
                summary = result.content if hasattr(result, 'content') else str(result)
                
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return self._fallback_summarization(messages)

    def _format_conversation_for_summarization(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format conversation messages for summarization.
        
        Args:
            messages (List[Dict]): List of conversation messages
            
        Returns:
            str: Formatted conversation text
        """
        formatted_messages = []
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # Format: Role: Content [Timestamp]
            formatted_msg = f"{role.capitalize()}: {content}"
            if timestamp:
                formatted_msg += f" [{timestamp}]"
            formatted_messages.append(formatted_msg)
            
        return "\n\n".join(formatted_messages)

    def _fallback_summarization(self, messages: List[Dict[str, Any]]) -> str:
        """
        Fallback summarization method when LLM is not available.
        
        Args:
            messages (List[Dict]): List of conversation messages
            
        Returns:
            str: Basic summary using heuristics
        """
        if not messages:
            return "No conversation to summarize."
            
        # Extract key information using simple heuristics
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
        
        summary_parts = []
        
        # Count message types
        summary_parts.append(f"Conversation contains {len(messages)} total messages")
        summary_parts.append(f"User messages: {len(user_messages)}")
        summary_parts.append(f"Assistant responses: {len(assistant_messages)}")
        
        # Extract key topics from user messages (first few words)
        if user_messages:
            topics = []
            for msg in user_messages[:5]:  # Look at first 5 user messages
                content = msg.get('content', '')
                if content:
                    # Extract first few words as topic
                    words = content.split()[:5]
                    topic = ' '.join(words)
                    if len(topic) > 10:  # Only add if meaningful
                        topics.append(topic)
            
            if topics:
                summary_parts.append(f"Key topics discussed: {'; '.join(topics)}")
        
        # Add timestamp information
        if messages:
            first_msg = messages[0]
            last_msg = messages[-1]
            if first_msg.get('timestamp') and last_msg.get('timestamp'):
                summary_parts.append(f"Conversation span: {first_msg['timestamp']} to {last_msg['timestamp']}")
        
        return " | ".join(summary_parts)

    def optimize_conversation_context(self, messages: List[Dict[str, Any]], 
                                   max_tokens: int = 8000) -> Tuple[List[Dict[str, Any]], str]:
        """
        Optimize conversation context by keeping recent messages and summarizing older ones.
        
        Args:
            messages (List[Dict]): Full conversation messages
            max_tokens (int): Maximum tokens to keep in context
            
        Returns:
            Tuple[List[Dict], str]: Optimized messages and summary of older conversation
        """
        if len(messages) <= self.max_detailed_messages * 2:  # No need to summarize
            return messages, ""
            
        # Keep the most recent messages in full detail
        recent_messages = messages[-(self.max_detailed_messages * 2):]
        
        # Get older messages for summarization
        older_messages = messages[:-(self.max_detailed_messages * 2)]
        
        # Create summary of older conversation
        summary = self.create_conversation_summary(older_messages)
        
        # Create summary message to represent older conversation
        summary_message = {
            'role': 'system',
            'content': f"Previous conversation summary: {summary}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {'type': 'conversation_summary', 'original_length': len(older_messages)}
        }
        
        # Combine summary with recent messages
        optimized_messages = [summary_message] + recent_messages
        
        return optimized_messages, summary

    async def optimize_conversation_context_async(self, messages: List[Dict[str, Any]], 
                                               max_tokens: int = 8000) -> Tuple[List[Dict[str, Any]], str]:
        """
        Async version of optimize_conversation_context.
        
        Args:
            messages (List[Dict]): Full conversation messages
            max_tokens (int): Maximum tokens to keep in context
            
        Returns:
            Tuple[List[Dict], str]: Optimized messages and summary of older conversation
        """
        if len(messages) <= self.max_detailed_messages * 2:  # No need to summarize
            return messages, ""
            
        # Keep the most recent messages in full detail
        recent_messages = messages[-(self.max_detailed_messages * 2):]
        
        # Get older messages for summarization
        older_messages = messages[:-(self.max_detailed_messages * 2)]
        
        # Create summary of older conversation using async method
        summary = await self.create_conversation_summary_async(older_messages)
        
        # Create summary message to represent older conversation
        summary_message = {
            'role': 'system',
            'content': f"Previous conversation summary: {summary}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {'type': 'conversation_summary', 'original_length': len(older_messages)}
        }
        
        # Combine summary with recent messages
        optimized_messages = [summary_message] + recent_messages
        
        return optimized_messages, summary

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text (str): Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def get_conversation_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the conversation for monitoring.
        
        Args:
            messages (List[Dict]): List of conversation messages
            
        Returns:
            Dict: Conversation statistics
        """
        if not messages:
            return {
                'total_messages': 0,
                'user_messages': 0,
                'assistant_messages': 0,
                'estimated_tokens': 0,
                'needs_summarization': False
            }
            
        user_count = len([msg for msg in messages if msg.get('role') == 'user'])
        assistant_count = len([msg for msg in messages if msg.get('role') == 'assistant'])
        
        # Estimate total tokens
        total_text = " ".join([msg.get('content', '') for msg in messages])
        estimated_tokens = self.estimate_tokens(total_text)
        
        # Check if summarization is needed
        message_pairs = min(user_count, assistant_count)
        needs_summarization = self.should_summarize(message_pairs, estimated_tokens)
        
        return {
            'total_messages': len(messages),
            'user_messages': user_count,
            'assistant_messages': assistant_count,
            'message_pairs': message_pairs,
            'estimated_tokens': estimated_tokens,
            'needs_summarization': needs_summarization,
            'context_window_usage': estimated_tokens / 32000  # Assuming 32k context window
        } 