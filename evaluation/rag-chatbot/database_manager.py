"""
RAGAS Evaluation Database Manager

This module provides a comprehensive interface for managing the RAGAS evaluation database.
It handles database initialization, CRUD operations, and data retrieval for evaluation purposes.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RAGASEvaluationDB:
    """Database manager for RAGAS evaluation data."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default path.
        """
        if db_path is None:
            db_path = Path(__file__).parent / "ragas_evaluation.db"
        
        self.db_path = str(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the schema."""
        try:
            # Read schema file
            schema_path = Path(__file__).parent / "database_schema.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
            
            logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    # ==================== EVALUATION SESSIONS ====================
    
    def create_session(self, session_name: str, description: str = None, 
                      created_by: str = None, llm_provider: str = None,
                      llm_model: str = None, search_mode: str = "standard") -> int:
        """
        Create a new evaluation session.
        
        Returns:
            int: Session ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluation_sessions 
                (session_name, description, created_by, llm_provider, llm_model, search_mode)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_name, description, created_by, llm_provider, llm_model, search_mode))
            return cursor.lastrowid
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get session details by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluation_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_sessions(self, status: str = None) -> List[Dict]:
        """List all sessions, optionally filtered by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM evaluation_sessions WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM evaluation_sessions ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_session_status(self, session_id: int, status: str):
        """Update session status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE evaluation_sessions SET status = ? WHERE id = ?", (status, session_id))
    
    # ==================== QUESTIONS ====================
    
    def add_question(self, session_id: int, question_text: str,
                    question_type: str = None, complexity_level: str = None,
                    expected_answer_type: str = None, domain_category: str = None) -> int:
        """
        Add a question to an evaluation session.
        
        Returns:
            int: Question ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO questions 
                (session_id, question_text, question_type, complexity_level, 
                 expected_answer_type, domain_category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, question_text, question_type, complexity_level,
                  expected_answer_type, domain_category))
            
            # Update session question count
            cursor.execute("""
                UPDATE evaluation_sessions 
                SET total_questions = (
                    SELECT COUNT(*) FROM questions WHERE session_id = ?
                ) WHERE id = ?
            """, (session_id, session_id))
            
            return cursor.lastrowid
    
    def get_questions_for_session(self, session_id: int) -> List[Dict]:
        """Get all questions for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE session_id = ? ORDER BY created_at", (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== RESPONSES ====================
    
    def add_response(self, question_id: int, llm_response: str,
                    conversation_id: str = None, response_time_ms: int = None,
                    total_tokens_used: int = None, search_mode_used: str = None,
                    selected_document_ids: List[str] = None) -> int:
        """
        Add an LLM response to a question.
        
        Returns:
            int: Response ID
        """
        selected_docs_json = json.dumps(selected_document_ids) if selected_document_ids else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO responses 
                (question_id, conversation_id, llm_response, response_time_ms,
                 total_tokens_used, search_mode_used, selected_document_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (question_id, conversation_id, llm_response, response_time_ms,
                  total_tokens_used, search_mode_used, selected_docs_json))
            
            return cursor.lastrowid
    
    def update_response_ground_truth(self, response_id: int, ground_truth_answer: str,
                                   human_evaluator: str = None):
        """Update response with ground truth answer."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE responses 
                SET ground_truth_answer = ?, human_evaluator = ?, evaluated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (ground_truth_answer, human_evaluator, response_id))
    
    def get_response(self, response_id: int) -> Optional[Dict]:
        """Get response details by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, q.question_text, q.session_id
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.id = ?
            """, (response_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== DOCUMENT CHUNKS ====================
    
    def add_document_chunk_used(self, response_id: int, chunk_content: str,
                               document_id: str = None, document_filename: str = None,
                               chunk_metadata: Dict = None, relevance_score: float = None,
                               chunk_order: int = None, was_cited: bool = False,
                               citation_quote: str = None) -> int:
        """
        Add a document chunk that was retrieved/used by the chatbot.
        
        Returns:
            int: Chunk ID
        """
        metadata_json = json.dumps(chunk_metadata) if chunk_metadata else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO document_chunks_used 
                (response_id, chunk_content, document_id, document_filename,
                 chunk_metadata, relevance_score, chunk_order, was_cited, citation_quote)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (response_id, chunk_content, document_id, document_filename,
                  metadata_json, relevance_score, chunk_order, was_cited, citation_quote))
            
            return cursor.lastrowid
    
    def add_expected_chunk(self, question_id: int, chunk_content: str,
                          document_id: str, document_filename: str,
                          chunk_metadata: Dict = None, relevance_level: str = "medium",
                          is_essential: bool = False, annotated_by: str = None,
                          annotation_notes: str = None) -> int:
        """
        Add an expected document chunk (human annotation).
        
        Returns:
            int: Expected chunk ID
        """
        metadata_json = json.dumps(chunk_metadata) if chunk_metadata else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expected_chunks 
                (question_id, chunk_content, document_id, document_filename,
                 chunk_metadata, relevance_level, is_essential, annotated_by, annotation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (question_id, chunk_content, document_id, document_filename,
                  metadata_json, relevance_level, is_essential, annotated_by, annotation_notes))
            
            return cursor.lastrowid
    
    def get_chunks_for_response(self, response_id: int) -> List[Dict]:
        """Get all chunks used for a response."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM document_chunks_used 
                WHERE response_id = ? 
                ORDER BY chunk_order
            """, (response_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_expected_chunks_for_question(self, question_id: int) -> List[Dict]:
        """Get all expected chunks for a question."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM expected_chunks 
                WHERE question_id = ? 
                ORDER BY relevance_level DESC, is_essential DESC
            """, (question_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== EVALUATION METRICS ====================
    
    def add_evaluation_metrics(self, response_id: int, metrics: Dict[str, Any],
                              evaluation_method: str = "ragas_auto",
                              evaluator: str = None, notes: str = None) -> int:
        """
        Add evaluation metrics for a response.
        
        Args:
            response_id: Response ID
            metrics: Dictionary containing metric scores
            evaluation_method: Method used for evaluation
            evaluator: Who performed the evaluation
            notes: Additional notes
            
        Returns:
            int: Metrics ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluation_metrics 
                (response_id, faithfulness_score, answer_relevancy_score, 
                 context_precision_score, context_recall_score, answer_similarity_score,
                 answer_correctness_score, chunks_retrieved_count, chunks_expected_count,
                 chunks_overlap_count, precision_at_k, recall_at_k,
                 human_relevance_score, human_accuracy_score, human_completeness_score,
                 human_clarity_score, evaluation_method, evaluator, evaluation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                response_id,
                metrics.get('faithfulness_score'),
                metrics.get('answer_relevancy_score'),
                metrics.get('context_precision_score'),
                metrics.get('context_recall_score'),
                metrics.get('answer_similarity_score'),
                metrics.get('answer_correctness_score'),
                metrics.get('chunks_retrieved_count'),
                metrics.get('chunks_expected_count'),
                metrics.get('chunks_overlap_count'),
                metrics.get('precision_at_k'),
                metrics.get('recall_at_k'),
                metrics.get('human_relevance_score'),
                metrics.get('human_accuracy_score'),
                metrics.get('human_completeness_score'),
                metrics.get('human_clarity_score'),
                evaluation_method,
                evaluator,
                notes
            ))
            
            return cursor.lastrowid
    
    def get_evaluation_metrics(self, response_id: int) -> Optional[Dict]:
        """Get evaluation metrics for a response."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluation_metrics WHERE response_id = ?", (response_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== FEEDBACK ====================
    
    def add_feedback(self, response_id: int, feedback_text: str,
                    feedback_type: str = "observation", category: str = None,
                    severity: str = "info", created_by: str = None) -> int:
        """Add evaluation feedback."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluation_feedback 
                (response_id, feedback_type, feedback_text, category, severity, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (response_id, feedback_type, feedback_text, category, severity, created_by))
            
            return cursor.lastrowid
    
    # ==================== ANALYSIS AND REPORTING ====================
    
    def get_session_summary(self, session_id: int) -> Dict:
        """Get comprehensive summary for a session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluation_summary WHERE session_name = (SELECT session_name FROM evaluation_sessions WHERE id = ?)", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def get_retrieval_performance(self, session_id: int = None) -> List[Dict]:
        """Get retrieval performance metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute("""
                    SELECT rp.* FROM retrieval_performance rp
                    JOIN responses r ON rp.response_id = r.id
                    JOIN questions q ON r.question_id = q.id
                    WHERE q.session_id = ?
                """, (session_id,))
            else:
                cursor.execute("SELECT * FROM retrieval_performance")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_session_data(self, session_id: int) -> Dict:
        """Export all data for a session in a structured format."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        questions = self.get_questions_for_session(session_id)
        
        # Get responses, chunks, and metrics for each question
        for question in questions:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get responses
                cursor.execute("SELECT * FROM responses WHERE question_id = ?", (question['id'],))
                responses = [dict(row) for row in cursor.fetchall()]
                
                for response in responses:
                    # Get chunks used
                    response['chunks_used'] = self.get_chunks_for_response(response['id'])
                    
                    # Get evaluation metrics
                    response['metrics'] = self.get_evaluation_metrics(response['id'])
                    
                    # Get feedback
                    cursor.execute("SELECT * FROM evaluation_feedback WHERE response_id = ?", (response['id'],))
                    response['feedback'] = [dict(row) for row in cursor.fetchall()]
                
                question['responses'] = responses
                
                # Get expected chunks
                question['expected_chunks'] = self.get_expected_chunks_for_question(question['id'])
        
        return {
            'session': session,
            'questions': questions,
            'summary': self.get_session_summary(session_id)
        }
    
    def close(self):
        """Close database connections (if needed for cleanup)."""
        pass  # sqlite3 connections are auto-closed with context managers


# ==================== HELPER FUNCTIONS ====================

def create_sample_session(db: RAGASEvaluationDB) -> int:
    """Create a sample evaluation session for testing."""
    session_id = db.create_session(
        session_name="Test Session 1",
        description="Initial testing of RAGAS evaluation system",
        created_by="System",
        llm_provider="groq",
        llm_model="llama-3.1-8b-instant",
        search_mode="standard"
    )
    
    # Add sample question
    question_id = db.add_question(
        session_id=session_id,
        question_text="What are the main benefits of renewable energy?",
        question_type="factual",
        complexity_level="medium",
        expected_answer_type="detailed",
        domain_category="environmental"
    )
    
    return session_id


if __name__ == "__main__":
    # Test the database
    db = RAGASEvaluationDB()
    session_id = create_sample_session(db)
    print(f"Created sample session with ID: {session_id}")
    
    # List sessions
    sessions = db.list_sessions()
    print(f"Total sessions: {len(sessions)}")
    for session in sessions:
        print(f"  - {session['session_name']} (ID: {session['id']})")
