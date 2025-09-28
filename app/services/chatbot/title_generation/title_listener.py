"""
PostgreSQL LISTEN/NOTIFY service for async title generation
Listens for title generation requests from database triggers and processes them with Groq API
"""

import asyncio
import json
import logging
import os
from typing import Optional
import asyncpg
from uuid import UUID

from app.services.chatbot.title_generation.title_generator import ConversationTitleGenerator
from app.db.conversations import Conversations
from app.core.config import settings
from app.core.database import db_manager

logger = logging.getLogger(__name__)


class TitleGenerationListener:
    """Listens for PostgreSQL notifications and generates titles with Groq API"""
    
    def __init__(self):
        self.title_generator = ConversationTitleGenerator()
        self.conversation_repo = Conversations(db_manager)
        self.connection: Optional[asyncpg.Connection] = None
        self.running = False
    
    async def connect(self):
        """Connect to PostgreSQL and start listening"""
        try:
            # Use database URL from settings
            db_url = settings.get_database_url()
            self.connection = await asyncpg.connect(db_url)
            
            # Listen for title generation requests
            await self.connection.add_listener('title_generation_request', self._handle_title_request)
            logger.info("Started listening for title generation requests")
            
        except Exception as e:
            logger.error(f"Failed to connect to database for title listening: {e}")
            raise
    
    async def _handle_title_request(self, connection, pid, channel, payload):
        """Handle title generation request from database trigger"""
        try:
            # Parse the notification payload
            data = json.loads(payload)
            conversation_id = UUID(data['conversation_id'])
            message = data['message']
            
            logger.info(f"Received title generation request for conversation {conversation_id}")
            
            # Generate title with Groq API (synchronous call)
            title = self.title_generator.generate_title_with_llm(message)
            
            if title and title != "New Chat":
                # Update conversation title in database
                self.conversation_repo.rename(conversation_id, title)
                logger.info(f"Updated conversation {conversation_id} with LLM title: {title}")
            else:
                logger.warning(f"Failed to generate LLM title for conversation {conversation_id}")
                
        except Exception as e:
            logger.error(f"Error processing title generation request: {e}")
    
    async def start_listening(self):
        """Start the listener loop"""
        self.running = True
        await self.connect()
        
        logger.info("Title generation listener started")
        
        try:
            while self.running:
                await asyncio.sleep(1)  # Keep the listener alive
        except asyncio.CancelledError:
            logger.info("Title generation listener cancelled")
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("Disconnected from PostgreSQL")
    
    def stop(self):
        """Stop the listener"""
        self.running = False


# Global listener instance
title_listener = TitleGenerationListener()


async def start_title_listener():
    """Start the title generation listener as a background task"""
    try:
        await title_listener.start_listening()
    except Exception as e:
        logger.error(f"Title listener failed: {e}")


def stop_title_listener():
    """Stop the title generation listener"""
    title_listener.stop()
