"""
Automatic conversation title generation service
Generates meaningful titles from user messages like ChatGPT/Claude using LLM
"""

import re
import logging
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ConversationTitleGenerator:
    """Generates conversation titles from user messages"""
    
    def __init__(self):
        # Initialize LLM clients
        self.groq_client = None
        self.gemini_client = None
        
        # Setup Groq - use your API key from .env
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        
        # Setup Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
        
        # Title generation prompt
        self.title_prompt = """Create a short, specific title that captures the main topic of this question. Focus on the key subject matter, not the question words.

Examples:
- "What are the company work hours?" → "Company Work Hours"
- "How do I analyze financial data?" → "Financial Data Analysis"
- "What was the Q4 revenue growth?" → "Q4 Revenue Growth"
- "Can you explain machine learning?" → "Machine Learning Explanation"

User message: "{message}"

Title (3-6 words, no question words):"""
        
        # Fallback patterns for when LLM fails
        self.fallback_patterns = [
            (r'(analyze|analysis)', 'Document Analysis'),
            (r'(how to|how do)', 'How-to Guide'),
            (r'(what is|explain)', 'Explanation'),
            (r'(compare|vs|versus)', 'Comparison'),
            (r'(create|generate|make)', 'Content Creation'),
            (r'(summary|summarize)', 'Summary Request'),
        ]
        
    def generate_title_with_llm(self, user_message: str) -> Optional[str]:
        """Generate title using Groq LLM"""
        if not user_message or not user_message.strip():
            logger.info("Empty user message for title generation")
            return None
            
        # Truncate very long messages for title generation
        message = user_message.strip()
        if len(message) > 200:
            message = message[:200] + "..."
        
        prompt = self.title_prompt.format(message=message)
        logger.info(f"Title generation prompt: {prompt[:100]}...")
        
        # Use Groq only
        if self.groq_client:
            try:
                logger.info("Calling Groq API for title generation")
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                    max_tokens=50
                )
                title = response.choices[0].message.content.strip()
                logger.info(f"Groq returned title: '{title}'")
                if title and len(title) < 80:
                    return title
            except Exception as e:
                logger.error(f"Groq title generation failed: {e}", exc_info=True)
        else:
            logger.warning("Groq client not initialized - check GROQ_API_KEY")
        
        return None
    
    def generate_fallback_title(self, user_message: str) -> str:
        """Generate title using pattern matching as fallback"""
        message = user_message.lower()
        
        # Check fallback patterns
        for pattern, title in self.fallback_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return title
        
        # Extract first few meaningful words
        words = re.findall(r'\b\w+\b', user_message)
        if words:
            # Skip common starting words
            skip_words = {'can', 'could', 'would', 'please', 'help', 'me', 'i', 'want', 'need', 'to'}
            meaningful_words = [w for w in words if w.lower() not in skip_words][:4]
            if meaningful_words:
                return ' '.join(meaningful_words).title()
        
        return "New Chat"
    
    def generate_title(self, user_message: str) -> str:
        """
        Generate a conversation title using LLM with fallback
        
        Args:
            user_message: The first user message in the conversation
            
        Returns:
            A clean, descriptive title for the conversation
        """
        try:
            if not user_message or not user_message.strip():
                return "New Chat"
            
            # Try LLM first
            llm_title = self.generate_title_with_llm(user_message)
            if llm_title:
                return llm_title
            
            # Fallback to pattern matching
            return self.generate_fallback_title(user_message)
            
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "New Chat"
    
    def generate_smart_title(self, user_message: str) -> str:
        """
        Alias for generate_title - now uses LLM by default
        
        Args:
            user_message: The first user message in the conversation
            
        Returns:
            A topic-focused title generated by LLM
        """
        return self.generate_title(user_message)


# Global instance
title_generator = ConversationTitleGenerator()


def generate_conversation_title(user_message: str, smart: bool = True) -> str:
    """
    Generate a conversation title from user message
    
    Args:
        user_message: The first user message
        smart: Whether to use smart topic extraction (default: True)
        
    Returns:
        Generated conversation title
    """
    if smart:
        return title_generator.generate_smart_title(user_message)
    else:
        return title_generator.generate_title(user_message)
