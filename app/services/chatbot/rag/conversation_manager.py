from typing import List, Dict, Optional
import json
from datetime import datetime


class ConversationManager:
    def __init__(self, max_history_length: int = 10):
        self.max_history_length = max_history_length
        self.conversations = {}

    def add_message(self, conversation_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.conversations[conversation_id].append(message)

        if len(self.conversations[conversation_id]) > self.max_history_length * 2:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history_length * 2:]

    def get_conversation_history(self, conversation_id: str,
                                 format_for_llm: bool = False) -> str:
        if conversation_id not in self.conversations:
            return ""

        messages = self.conversations[conversation_id]

        if format_for_llm:
            formatted_history = []
            for msg in messages[-self.max_history_length:]:
                role_name = "Human" if msg['role'] == 'user' else "Assistant"
                formatted_history.append(f"{role_name}: {msg['content']}")
            return "\n".join(formatted_history)

        return json.dumps(messages, indent=2)