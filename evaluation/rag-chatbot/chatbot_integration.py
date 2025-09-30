"""
Chatbot Integration for RAGAS Evaluation

This module provides integration between the existing chatbot system and the RAGAS evaluation database.
It captures chatbot interactions, document chunks, and responses for evaluation purposes.
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from database_manager import RAGASEvaluationDB

logger = logging.getLogger(__name__)

class ChatbotEvaluationCapture:
    """
    Captures chatbot interactions for RAGAS evaluation.
    
    This class acts as a middleware between the chatbot and the evaluation database,
    automatically recording questions, responses, and document chunks for later evaluation.
    """
    
    def __init__(self, db_path: str = None, session_id: int = None):
        """
        Initialize the evaluation capture system.
        
        Args:
            db_path: Path to the evaluation database
            session_id: Active evaluation session ID (if None, creates new session)
        """
        self.db = RAGASEvaluationDB(db_path)
        self.session_id = session_id
        self.active_captures = {}  # Track ongoing captures by conversation_id
        
    def start_session(self, session_name: str, description: str = None,
                     llm_provider: str = None, llm_model: str = None,
                     search_mode: str = "standard", created_by: str = None) -> int:
        """
        Start a new evaluation session.
        
        Returns:
            int: Session ID
        """
        self.session_id = self.db.create_session(
            session_name=session_name,
            description=description,
            created_by=created_by,
            llm_provider=llm_provider,
            llm_model=llm_model,
        )
        logger.info(f"Started evaluation session {self.session_id}: {session_name}")
        return self.session_id
    
    def capture_question(self, question_text: str, conversation_id: str = None,
                        document_type: str = None,
                        expected_answer_type: str = None, domain_category: str = None) -> int:
        """
        Capture a question for evaluation.
        
        Args:
            question_text: The user's question
            conversation_id: Unique conversation identifier
            document_type: Type of document (research_paper, invoice, etc.)
            expected_answer_type: Expected answer format
            domain_category: Domain/category of the question
            
        Returns:
            int: Question ID
        """
        question_id = self.db.add_question(
            session_id=self.session_id,
            question_text=question_text,
            document_type=document_type,
            expected_answer_type=expected_answer_type,
            domain_category=domain_category
        )
        
        # Initialize capture tracking
        if conversation_id:
            self.active_captures[conversation_id] = {
                'question_id': question_id,
                'start_time': time.time(),
                'chunks_captured': []
            }
        
        logger.info(f"Captured question {question_id}: {question_text[:50]}...")
        return question_id
    
    def capture_response_with_chunks(self, question_id: int, llm_response: str,
                                   document_chunks: List[Dict], conversation_id: str = None,
                                   response_time_ms: int = None, total_tokens_used: int = None,
                                   search_mode_used: str = None, selected_document_ids: List[str] = None) -> int:
        """
        Capture an LLM response along with the document chunks that were retrieved.
        
        Args:
            question_id: Question ID this response answers
            llm_response: The generated response text
            document_chunks: List of document chunks retrieved by the chatbot
            conversation_id: Conversation identifier
            response_time_ms: Time taken to generate response
            total_tokens_used: Total tokens used
            search_mode_used: Search mode that was used
            selected_document_ids: Document IDs if Knowledge Base mode was used
            
        Returns:
            int: Response ID
        """
        # Add the response
        response_id = self.db.add_response(
            question_id=question_id,
            llm_response=llm_response,
            conversation_id=conversation_id,
            response_time_ms=response_time_ms,
            total_tokens_used=total_tokens_used,
            search_mode_used=search_mode_used,
            selected_document_ids=selected_document_ids
        )
        
        # Add document chunks
        for i, chunk in enumerate(document_chunks):
            self.db.add_document_chunk_used(
                response_id=response_id,
                chunk_content=chunk.get('content', chunk.get('page_content', '')),
                document_id=chunk.get('metadata', {}).get('document_id'),
                document_filename=chunk.get('metadata', {}).get('filename'),
                chunk_metadata=chunk.get('metadata', {}),
                relevance_score=chunk.get('score', chunk.get('metadata', {}).get('score')),
                chunk_order=i + 1,
                was_cited=chunk.get('was_cited', False),
                citation_quote=chunk.get('quote', chunk.get('citation_quote'))
            )
        
        logger.info(f"Captured response {response_id} with {len(document_chunks)} chunks")
        return response_id
    
    def capture_from_chat_engine_result(self, question_text: str, chat_result: Dict,
                                      conversation_id: str = None, start_time: float = None,
                                      question_metadata: Dict = None) -> Dict[str, int]:
        """
        Capture data directly from chat engine result (from process_query or streaming).
        
        This method automatically extracts all relevant information from the chatbot's
        response format and stores it in the evaluation database.
        
        Args:
            question_text: The original question
            chat_result: Result from chat_engine.process_query()
            conversation_id: Conversation ID
            start_time: Start time for response time calculation
            question_metadata: Additional metadata about the question
            
        Returns:
            Dict containing question_id and response_id
        """
        if not self.session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        # Calculate response time
        response_time_ms = None
        if start_time:
            response_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract question metadata
        q_meta = question_metadata or {}
        
        # Capture question
        question_id = self.capture_question(
            question_text=question_text,
            conversation_id=conversation_id,
            document_type=q_meta.get('document_type'),
            expected_answer_type=q_meta.get('expected_answer_type'),
            domain_category=q_meta.get('domain_category')
        )
        
        # Extract document chunks from sources
        document_chunks = []
        sources = chat_result.get('sources', [])
        
        for source in sources:
            chunk_data = {
                'content': source.get('content', ''),
                'page_content': source.get('content', ''),  # Alternative key
                'metadata': source.get('metadata', {}),
                'score': source.get('score', 0),
                'was_cited': 'quote' in source,  # If there's a quote, it was cited
                'quote': source.get('quote', ''),
                'citation_quote': source.get('quote', '')
            }
            document_chunks.append(chunk_data)
        
        # Capture response with chunks
        response_id = self.capture_response_with_chunks(
            question_id=question_id,
            llm_response=chat_result.get('response', ''),
            document_chunks=document_chunks,
            conversation_id=conversation_id,
            response_time_ms=response_time_ms,
            search_mode_used=q_meta.get('search_mode', 'standard')
        )
        
        return {
            'question_id': question_id,
            'response_id': response_id,
            'chunks_count': len(document_chunks)
        }
    
    def add_ground_truth(self, response_id: int, ground_truth_answer: str,
                        human_evaluator: str = None):
        """Add ground truth answer for a response."""
        self.db.update_response_ground_truth(
            response_id=response_id,
            ground_truth_answer=ground_truth_answer,
            human_evaluator=human_evaluator
        )
        logger.info(f"Added ground truth for response {response_id}")
    
    def add_expected_chunks(self, question_id: int, expected_chunks: List[Dict]):
        """
        Add expected document chunks for a question (human annotation).
        
        Args:
            question_id: Question ID
            expected_chunks: List of expected chunks with metadata
        """
        for chunk in expected_chunks:
            self.db.add_expected_chunk(
                question_id=question_id,
                chunk_content=chunk['content'],
                document_id=chunk['document_id'],
                document_filename=chunk['document_filename'],
                chunk_metadata=chunk.get('metadata'),
                relevance_level=chunk.get('relevance_level', 'medium'),
                is_essential=chunk.get('is_essential', False),
                annotated_by=chunk.get('annotated_by'),
                annotation_notes=chunk.get('annotation_notes')
            )
        logger.info(f"Added {len(expected_chunks)} expected chunks for question {question_id}")
    
    def get_session_data(self) -> Dict:
        """Get all data for the current session."""
        if not self.session_id:
            return {}
        return self.db.export_session_data(self.session_id)
    
    def get_unevaluated_responses(self) -> List[Dict]:
        """Get responses that don't have ground truth yet."""
        if not self.session_id:
            return []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, q.question_text 
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE q.session_id = ? AND r.ground_truth_answer IS NULL
                ORDER BY r.created_at
            """, (self.session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_questions_without_expected_chunks(self) -> List[Dict]:
        """Get questions that don't have expected chunks annotated yet."""
        if not self.session_id:
            return []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.* FROM questions q
                WHERE q.session_id = ? 
                AND q.id NOT IN (SELECT DISTINCT question_id FROM expected_chunks)
                ORDER BY q.created_at
            """, (self.session_id,))
            return [dict(row) for row in cursor.fetchall()]


# ==================== DECORATOR FOR AUTOMATIC CAPTURE ====================

class AutoCaptureDecorator:
    """
    Decorator to automatically capture chatbot interactions.
    
    Usage:
        @auto_capture_decorator.capture_interaction
        async def process_query(self, query, conversation_id=None, ...):
            # Your existing chatbot code
            return result
    """
    
    def __init__(self, capture_system: ChatbotEvaluationCapture):
        self.capture = capture_system
    
    def capture_interaction(self, func):
        """Decorator to automatically capture chatbot interactions."""
        async def wrapper(*args, **kwargs):
            # Extract question from arguments
            question_text = None
            conversation_id = None
            
            # Try to find question in args/kwargs
            if len(args) > 1:
                question_text = args[1]  # Assuming second arg is query
            elif 'query' in kwargs:
                question_text = kwargs['query']
            elif 'question' in kwargs:
                question_text = kwargs['question']
            
            # Try to find conversation_id
            if 'conversation_id' in kwargs:
                conversation_id = kwargs['conversation_id']
            
            start_time = time.time()
            
            # Call original function
            result = await func(*args, **kwargs)
            
            # Capture the interaction if we have the required data
            if question_text and isinstance(result, dict):
                try:
                    capture_result = self.capture.capture_from_chat_engine_result(
                        question_text=question_text,
                        chat_result=result,
                        conversation_id=conversation_id,
                        start_time=start_time
                    )
                    logger.info(f"Auto-captured interaction: {capture_result}")
                except Exception as e:
                    logger.error(f"Failed to auto-capture interaction: {e}")
            
            return result
        
        return wrapper


# ==================== CONVENIENCE FUNCTIONS ====================

def create_evaluation_session(session_name: str, llm_provider: str = "groq",
                            llm_model: str = "llama-3.1-8b-instant",
                            description: str = None) -> ChatbotEvaluationCapture:
    """
    Convenience function to create a new evaluation session.
    
    Returns:
        ChatbotEvaluationCapture: Configured capture system
    """
    capture = ChatbotEvaluationCapture()
    session_id = capture.start_session(
        session_name=session_name,
        description=description,
        llm_provider=llm_provider,
        llm_model=llm_model,
        created_by="System"
    )
    return capture

def load_evaluation_session(session_id: int) -> ChatbotEvaluationCapture:
    """
    Load an existing evaluation session.
    
    Returns:
        ChatbotEvaluationCapture: Configured capture system
    """
    capture = ChatbotEvaluationCapture(session_id=session_id)
    return capture


if __name__ == "__main__":
    # Example usage
    capture = create_evaluation_session(
        session_name="Test Evaluation Session",
        description="Testing the capture system"
    )
    
    # Simulate a chatbot interaction
    sample_result = {
        'conversation_id': str(uuid.uuid4()),
        'response': 'This is a sample response about renewable energy benefits.',
        'sources': [
            {
                'content': 'Renewable energy sources like solar and wind...',
                'metadata': {
                    'document_id': 'doc_123',
                    'filename': 'renewable_energy.pdf',
                    'score': 0.85
                },
                'score': 0.85,
                'quote': 'solar and wind energy are sustainable'
            }
        ]
    }
    
    result = capture.capture_from_chat_engine_result(
        question_text="What are the benefits of renewable energy?",
        chat_result=sample_result,
        question_metadata={'question_type': 'factual', 'complexity_level': 'medium'}
    )
    
    print(f"Captured interaction: {result}")
    
    # Get session data
    session_data = capture.get_session_data()
    print(f"Session has {len(session_data.get('questions', []))} questions")
