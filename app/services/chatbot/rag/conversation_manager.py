from typing import List, Dict, Optional, Tuple, Any
import json
from datetime import datetime
from .conversation_summarizer import ConversationSummarizer


class ConversationManager:
    """
    A conversation manager for handling chat history and message storage.
    
    This class provides functionality for managing conversation history across
    multiple chat sessions. It supports:
    - Adding messages with metadata to specific conversations
    - Retrieving conversation history in different formats
    - Automatic history length management to prevent memory bloat
    - LLM-friendly formatting for context injection
    
    The manager is designed to work with chat applications that need to
    maintain conversation state across multiple user interactions.
    """
    
    def __init__(self, max_history_length: int = 10, enable_summarization: bool = True):
        """
        Args:
            max_history_length (int): Maximum number of message pairs to keep in history.
                                    Each conversation turn consists of a user message and
                                    an assistant response, so this effectively controls
                                    the number of conversation turns to remember.
            enable_summarization (bool): Whether to enable conversation summarization
        """
        self.max_history_length = max_history_length
        self.enable_summarization = enable_summarization
        # Store conversations indexed by conversation ID
        self.conversations = {}
        
        # Initialize conversation summarizer if enabled
        self.summarizer = ConversationSummarizer() if enable_summarization else None

    def add_message(self, conversation_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None):
        """
        Add a message to a specific conversation.
        
        This method adds a new message to the conversation history, automatically
        managing the conversation length to prevent memory issues. Messages are
        stored with timestamps and optional metadata for tracking and debugging.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            role (str): Role of the message sender ('user' or 'assistant')
            content (str): The message content
            metadata (Optional[Dict]): Optional metadata to store with the message
        """
        # Create conversation list if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        # Create message object with timestamp and metadata
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),  # ISO format for easy parsing
            'metadata': metadata or {}  # Use empty dict if no metadata provided
        }

        # Add message to conversation history
        self.conversations[conversation_id].append(message)

        # Check if summarization is needed
        if self.enable_summarization and self.summarizer:
            conversation_stats = self.summarizer.get_conversation_stats(self.conversations[conversation_id])
            
            if conversation_stats['needs_summarization']:
                # Optimize conversation context by summarizing older messages
                optimized_messages, summary = self.summarizer.optimize_conversation_context(
                    self.conversations[conversation_id]
                )
                self.conversations[conversation_id] = optimized_messages
                
                # Log summarization for monitoring
                print(f"Conversation {conversation_id} summarized. Original: {conversation_stats['total_messages']} messages, "
                      f"Optimized: {len(optimized_messages)} messages")
        else:
            # Fallback to simple truncation if summarization is disabled
            # Keep twice the max_history_length to account for user/assistant message pairs
            if len(self.conversations[conversation_id]) > self.max_history_length * 2:
                # Keep only the most recent messages
                self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history_length * 2:]

    def get_conversation_history(self, conversation_id: str,
                                 format_for_llm: bool = False) -> str:
        """
        Retrieve conversation history for a specific conversation.
        
        This method returns the conversation history in different formats depending
        on the intended use. It can return either a JSON string for storage/transmission
        or a formatted string suitable for LLM context injection.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            format_for_llm (bool): If True, format history as LLM-friendly text.
                                  If False, return JSON string format.
            
        Returns:
            str: Conversation history in the requested format.
                 Returns empty string if conversation doesn't exist.
        """
        # Return empty string if conversation doesn't exist
        if conversation_id not in self.conversations:
            return ""

        messages = self.conversations[conversation_id]

        if format_for_llm:
            # Format messages for LLM context injection
            # This creates a human-readable conversation format
            formatted_history = []
            
            # Include all messages (including summaries) for LLM context
            for msg in messages:
                # Map roles to LLM-friendly names
                if msg['role'] == 'system' and msg.get('metadata', {}).get('type') == 'conversation_summary':
                    # Format summary messages specially
                    formatted_history.append(f"System: {msg['content']}")
                else:
                    role_name = "Human" if msg['role'] == 'user' else "Assistant"
                    formatted_history.append(f"{role_name}: {msg['content']}")
                    
            return "\n".join(formatted_history)

        # Return JSON format for storage or transmission
        return json.dumps(messages, indent=2)

    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get statistics about a specific conversation.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            
        Returns:
            Dict[str, Any]: Conversation statistics including token estimates and summarization status
        """
        if conversation_id not in self.conversations:
            return {}
            
        if self.summarizer:
            return self.summarizer.get_conversation_stats(self.conversations[conversation_id])
        else:
            # Basic stats without summarization
            messages = self.conversations[conversation_id]
            user_count = len([msg for msg in messages if msg.get('role') == 'user'])
            assistant_count = len([msg for msg in messages if msg.get('role') == 'assistant'])
            
            return {
                'total_messages': len(messages),
                'user_messages': user_count,
                'assistant_messages': assistant_count,
                'message_pairs': min(user_count, assistant_count),
                'estimated_tokens': len(" ".join([msg.get('content', '') for msg in messages])) // 4,
                'needs_summarization': False,
                'summarization_enabled': False
            }

    def force_summarization(self, conversation_id: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Force summarization of a conversation regardless of thresholds.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            
        Returns:
            Tuple[List[Dict], str]: Optimized messages and summary
        """
        if not self.enable_summarization or not self.summarizer:
            return self.conversations.get(conversation_id, []), ""
            
        if conversation_id not in self.conversations:
            return [], ""
            
        # Force summarization
        optimized_messages, summary = self.summarizer.optimize_conversation_context(
            self.conversations[conversation_id]
        )
        self.conversations[conversation_id] = optimized_messages
        
        return optimized_messages, summary

    def clear_conversation(self, conversation_id: str):
        """
        Clear a specific conversation.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

    def get_all_conversation_ids(self) -> List[str]:
        """
        Get all active conversation IDs.
        
        Returns:
            List[str]: List of active conversation IDs
        """
        return list(self.conversations.keys())