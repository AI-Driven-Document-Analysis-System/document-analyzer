from typing import List, Dict, Optional
import json
from datetime import datetime


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
    
    def __init__(self, max_history_length: int = 10):
        """
        Args:
            max_history_length (int): Maximum number of message pairs to keep in history.
                                    Each conversation turn consists of a user message and
                                    an assistant response, so this effectively controls
                                    the number of conversation turns to remember.
        """
        self.max_history_length = max_history_length
        # Store conversations indexed by conversation ID
        self.conversations = {}

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

        # Manage conversation length to prevent memory bloat
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
            for msg in messages[-self.max_history_length:]:  # Use only recent messages
                # Map roles to LLM-friendly names
                role_name = "Human" if msg['role'] == 'user' else "Assistant"
                formatted_history.append(f"{role_name}: {msg['content']}")
            return "\n".join(formatted_history)

        # Return JSON format for storage or transmission
        return json.dumps(messages, indent=2)