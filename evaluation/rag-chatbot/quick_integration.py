"""
Quick integration script to start capturing chatbot data for RAGAS evaluation.

Add this to your existing chatbot to automatically record interactions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from chatbot_integration import ChatbotEvaluationCapture
from config_manager import get_ragas_config, is_ragas_enabled
import time

# Global evaluation capture instance
evaluation_capture = None

def init_evaluation_capture(session_name: str = None):
    """Initialize evaluation capture for the current session."""
    global evaluation_capture
    
    # Check if evaluation is enabled
    if not is_ragas_enabled():
        print("RAGAS evaluation is disabled in .testing config")
        return None
    
    config = get_ragas_config()
    
    # Use config values if not provided
    if session_name is None:
        session_name = config.get_session_name()
    
    evaluation_capture = ChatbotEvaluationCapture(db_path=config.get_db_path())
    session_id = evaluation_capture.start_session(
        session_name=session_name,
        description=config.get_session_description(),
        llm_provider="groq",  # Update based on your setup
        llm_model="llama-3.1-8b-instant",  # Update based on your setup
        created_by="System"
    )
    
    if config.is_verbose_logging_enabled():
        print(f"✓ Started evaluation session {session_id}: {session_name}")
    
    return session_id

def capture_chatbot_interaction(question: str, chat_result: dict, 
                               conversation_id: str = None, start_time: float = None):
    """
    Capture a single chatbot interaction.
    
    Call this after your chatbot processes a query.
    
    Args:
        question: The user's question
        chat_result: Result from chat_engine.process_query() or similar
        conversation_id: Conversation ID
        start_time: Start time for response calculation
    """
    global evaluation_capture
    
    # Check if evaluation is enabled
    if not is_ragas_enabled():
        return None
    
    if not evaluation_capture:
        session_id = init_evaluation_capture()
        if session_id is None:
            return None
    
    try:
        result = evaluation_capture.capture_from_chat_engine_result(
            question_text=question,
            chat_result=chat_result,
            conversation_id=conversation_id,
            start_time=start_time
        )
        
        config = get_ragas_config()
        if config.is_verbose_logging_enabled():
            print(f"✓ Captured: Q{result['question_id']}, R{result['response_id']}, {result['chunks_count']} chunks")
        
        return result
    except Exception as e:
        config = get_ragas_config()
        if config.is_verbose_logging_enabled():
            print(f"❌ Failed to capture interaction: {e}")
        return None

def get_evaluation_stats():
    """Get current evaluation statistics."""
    global evaluation_capture
    
    if not evaluation_capture:
        return "No active evaluation session"
    
    session_data = evaluation_capture.get_session_data()
    questions = session_data.get('questions', [])
    
    stats = {
        'session_id': evaluation_capture.session_id,
        'total_questions': len(questions),
        'total_responses': sum(len(q.get('responses', [])) for q in questions),
        'unevaluated_responses': len(evaluation_capture.get_unevaluated_responses()),
        'questions_without_expected_chunks': len(evaluation_capture.get_questions_without_expected_chunks())
    }
    
    return stats

# Example usage functions
def example_integration_with_existing_chatbot():
    """
    Example of how to integrate with your existing chatbot.
    
    Add these lines to your chatbot processing function:
    """
    
    # At the start of your chat processing:
    # start_time = time.time()
    
    # After getting the result from your chat engine:
    # capture_chatbot_interaction(
    #     question=user_question,
    #     chat_result=result_from_chat_engine,
    #     conversation_id=conversation_id,
    #     start_time=start_time
    # )
    
    pass

if __name__ == "__main__":
    # Test the integration
    print("Testing RAGAS evaluation integration...")
    
    # Initialize
    session_id = init_evaluation_capture("Test Integration Session")
    
    # Simulate a chatbot interaction
    sample_question = "What are the benefits of renewable energy?"
    sample_result = {
        'conversation_id': 'test-conv-123',
        'response': 'Renewable energy provides environmental and economic benefits...',
        'sources': [
            {
                'content': 'Solar power reduces carbon emissions significantly.',
                'metadata': {
                    'document_id': 'doc_001',
                    'filename': 'renewable_energy.pdf'
                },
                'score': 0.9,
                'quote': 'reduces carbon emissions'
            }
        ]
    }
    
    # Capture the interaction
    result = capture_chatbot_interaction(
        question=sample_question,
        chat_result=sample_result,
        conversation_id='test-conv-123',
        start_time=time.time() - 2  # Simulate 2 second response time
    )
    
    # Show stats
    stats = get_evaluation_stats()
    print(f"Evaluation stats: {stats}")
    
    print("✓ Integration test completed!")
