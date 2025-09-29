"""
Test script for the RAGAS evaluation database system.

This script demonstrates how to use the database and creates sample data for testing.
"""

import uuid
import json
from database_manager import RAGASEvaluationDB
from chatbot_integration import ChatbotEvaluationCapture, create_evaluation_session

def test_database_creation():
    """Test database creation and basic operations."""
    print("=== Testing Database Creation ===")
    
    # Initialize database
    db = RAGASEvaluationDB()
    print("✓ Database initialized successfully")
    
    # Create a test session
    session_id = db.create_session(
        session_name="Test Session - Database Creation",
        description="Testing basic database functionality",
        created_by="Test Script",
        llm_provider="groq",
        llm_model="llama-3.1-8b-instant"
    )
    print(f"✓ Created test session with ID: {session_id}")
    
    # Add a test question
    question_id = db.add_question(
        session_id=session_id,
        question_text="What is artificial intelligence?",
        question_type="factual",
        complexity_level="simple",
        expected_answer_type="detailed",
        domain_category="technology"
    )
    print(f"✓ Added test question with ID: {question_id}")
    
    # Add a test response
    response_id = db.add_response(
        question_id=question_id,
        llm_response="Artificial intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior.",
        conversation_id=str(uuid.uuid4()),
        response_time_ms=1500,
        total_tokens_used=45,
        search_mode_used="standard"
    )
    print(f"✓ Added test response with ID: {response_id}")
    
    # Add test document chunks
    chunk_id = db.add_document_chunk_used(
        response_id=response_id,
        chunk_content="Artificial intelligence is the simulation of human intelligence in machines...",
        document_id="doc_ai_001",
        document_filename="ai_introduction.pdf",
        chunk_metadata={"page": 1, "section": "Introduction"},
        relevance_score=0.92,
        chunk_order=1,
        was_cited=True,
        citation_quote="simulation of human intelligence in machines"
    )
    print(f"✓ Added test document chunk with ID: {chunk_id}")
    
    # Add expected chunk
    expected_id = db.add_expected_chunk(
        question_id=question_id,
        chunk_content="AI definition from authoritative source...",
        document_id="doc_ai_001",
        document_filename="ai_introduction.pdf",
        relevance_level="high",
        is_essential=True,
        annotated_by="Human Expert",
        annotation_notes="This is the standard definition"
    )
    print(f"✓ Added expected chunk with ID: {expected_id}")
    
    # Add evaluation metrics
    metrics = {
        'faithfulness_score': 0.85,
        'answer_relevancy_score': 0.90,
        'context_precision_score': 0.88,
        'context_recall_score': 0.75,
        'chunks_retrieved_count': 3,
        'chunks_expected_count': 2,
        'chunks_overlap_count': 1,
        'human_relevance_score': 4,
        'human_accuracy_score': 5
    }
    
    metrics_id = db.add_evaluation_metrics(
        response_id=response_id,
        metrics=metrics,
        evaluation_method="ragas_auto",
        evaluator="Test System"
    )
    print(f"✓ Added evaluation metrics with ID: {metrics_id}")
    
    return session_id

def test_chatbot_integration():
    """Test the chatbot integration system."""
    print("\n=== Testing Chatbot Integration ===")
    
    # Create evaluation session
    capture = create_evaluation_session(
        session_name="Test Session - Chatbot Integration",
        description="Testing chatbot integration functionality",
        llm_provider="groq",
        llm_model="llama-3.1-8b-instant"
    )
    print(f"✓ Created evaluation session: {capture.session_id}")
    
    # Simulate chatbot result
    sample_chat_result = {
        'conversation_id': str(uuid.uuid4()),
        'response': '''# Benefits of Renewable Energy

Renewable energy offers several key advantages:

## Environmental Benefits
- **Reduced Carbon Emissions**: Solar and wind power produce no direct emissions
- **Sustainable Resource**: Unlike fossil fuels, renewable sources are naturally replenished

## Economic Benefits  
- **Job Creation**: The renewable sector creates more jobs per dollar invested
- **Energy Independence**: Reduces reliance on imported fossil fuels

## Long-term Advantages
- **Cost Stability**: Renewable energy costs are becoming increasingly competitive
- **Technology Advancement**: Continuous improvements in efficiency and storage''',
        'sources': [
            {
                'content': 'Solar and wind power are clean energy sources that produce no direct carbon emissions during operation. They help reduce greenhouse gas emissions significantly.',
                'metadata': {
                    'document_id': 'doc_renewable_001',
                    'filename': 'renewable_energy_benefits.pdf',
                    'page': 3,
                    'section': 'Environmental Impact'
                },
                'score': 0.92,
                'quote': 'Solar and wind power produce no direct emissions',
                'title': 'renewable_energy_benefits.pdf',
                'type': 'document'
            },
            {
                'content': 'The renewable energy sector has been a significant job creator, with solar and wind industries leading employment growth in the energy sector.',
                'metadata': {
                    'document_id': 'doc_renewable_002', 
                    'filename': 'green_jobs_report.pdf',
                    'page': 12,
                    'section': 'Employment Statistics'
                },
                'score': 0.87,
                'quote': 'renewable sector creates more jobs per dollar invested',
                'title': 'green_jobs_report.pdf',
                'type': 'document'
            },
            {
                'content': 'Renewable energy technologies have achieved cost parity with fossil fuels in many markets, with costs continuing to decline due to technological improvements.',
                'metadata': {
                    'document_id': 'doc_renewable_003',
                    'filename': 'energy_cost_analysis.pdf', 
                    'page': 8,
                    'section': 'Cost Trends'
                },
                'score': 0.83,
                'quote': 'costs are becoming increasingly competitive',
                'title': 'energy_cost_analysis.pdf',
                'type': 'document'
            }
        ],
        'chat_history': []
    }
    
    # Capture the interaction
    result = capture.capture_from_chat_engine_result(
        question_text="What are the main benefits of renewable energy sources?",
        chat_result=sample_chat_result,
        question_metadata={
            'question_type': 'factual',
            'complexity_level': 'medium',
            'expected_answer_type': 'detailed',
            'domain_category': 'environmental'
        }
    )
    
    print(f"✓ Captured interaction - Question ID: {result['question_id']}, Response ID: {result['response_id']}")
    print(f"✓ Captured {result['chunks_count']} document chunks")
    
    # Add ground truth
    capture.add_ground_truth(
        response_id=result['response_id'],
        ground_truth_answer="""Renewable energy sources offer three main categories of benefits:

1. Environmental: Zero direct emissions, reduced carbon footprint, sustainable resource utilization
2. Economic: Job creation, energy independence, long-term cost savings
3. Technological: Improving efficiency, declining costs, energy storage advances

These benefits make renewable energy crucial for sustainable development and climate change mitigation.""",
        human_evaluator="Domain Expert"
    )
    print("✓ Added ground truth answer")
    
    # Add expected chunks
    expected_chunks = [
        {
            'content': 'Solar and wind power are clean energy sources that produce no direct carbon emissions during operation.',
            'document_id': 'doc_renewable_001',
            'document_filename': 'renewable_energy_benefits.pdf',
            'metadata': {'page': 3, 'section': 'Environmental Impact'},
            'relevance_level': 'high',
            'is_essential': True,
            'annotated_by': 'Domain Expert',
            'annotation_notes': 'Core environmental benefit - essential for complete answer'
        },
        {
            'content': 'The renewable energy sector has been a significant job creator in recent years.',
            'document_id': 'doc_renewable_002',
            'document_filename': 'green_jobs_report.pdf',
            'metadata': {'page': 12, 'section': 'Employment Statistics'},
            'relevance_level': 'high',
            'is_essential': True,
            'annotated_by': 'Domain Expert',
            'annotation_notes': 'Economic benefit - job creation is a key advantage'
        }
    ]
    
    capture.add_expected_chunks(result['question_id'], expected_chunks)
    print(f"✓ Added {len(expected_chunks)} expected chunks")
    
    return capture.session_id

def test_data_retrieval(session_id):
    """Test data retrieval and analysis functions."""
    print(f"\n=== Testing Data Retrieval for Session {session_id} ===")
    
    db = RAGASEvaluationDB()
    
    # Get session summary
    summary = db.get_session_summary(session_id)
    print("✓ Session Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Get questions for session
    questions = db.get_questions_for_session(session_id)
    print(f"✓ Found {len(questions)} questions in session")
    
    # Get retrieval performance
    performance = db.get_retrieval_performance(session_id)
    print(f"✓ Retrieved performance data for {len(performance)} responses")
    
    # Export full session data
    export_data = db.export_session_data(session_id)
    print(f"✓ Exported session data with {len(export_data.get('questions', []))} questions")
    
    return export_data

def create_comprehensive_test_data():
    """Create a comprehensive set of test data."""
    print("\n=== Creating Comprehensive Test Data ===")
    
    capture = create_evaluation_session(
        session_name="Comprehensive Test Dataset",
        description="Full test dataset with multiple question types and scenarios",
        llm_provider="groq",
        llm_model="llama-3.1-8b-instant"
    )
    
    # Test questions with different characteristics
    test_scenarios = [
        {
            'question': 'What is machine learning?',
            'type': 'factual',
            'complexity': 'simple',
            'domain': 'technology',
            'response': 'Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.',
            'chunks_count': 2
        },
        {
            'question': 'Compare supervised and unsupervised learning approaches in detail.',
            'type': 'comparative',
            'complexity': 'complex', 
            'domain': 'technology',
            'response': 'Supervised learning uses labeled data to train models, while unsupervised learning finds patterns in unlabeled data...',
            'chunks_count': 4
        },
        {
            'question': 'How does climate change affect biodiversity?',
            'type': 'analytical',
            'complexity': 'medium',
            'domain': 'environmental',
            'response': 'Climate change impacts biodiversity through habitat loss, species migration, and ecosystem disruption...',
            'chunks_count': 3
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        # Create mock chat result
        sources = []
        for j in range(scenario['chunks_count']):
            sources.append({
                'content': f"Sample chunk {j+1} content for {scenario['question'][:30]}...",
                'metadata': {
                    'document_id': f"doc_{scenario['domain']}_{j+1:03d}",
                    'filename': f"{scenario['domain']}_document_{j+1}.pdf",
                    'page': j+1,
                    'section': f"Section {j+1}"
                },
                'score': 0.9 - (j * 0.1),
                'quote': f"key quote from chunk {j+1}",
                'title': f"{scenario['domain']}_document_{j+1}.pdf",
                'type': 'document'
            })
        
        chat_result = {
            'conversation_id': str(uuid.uuid4()),
            'response': scenario['response'],
            'sources': sources,
            'chat_history': []
        }
        
        # Capture interaction
        result = capture.capture_from_chat_engine_result(
            question_text=scenario['question'],
            chat_result=chat_result,
            question_metadata={
                'question_type': scenario['type'],
                'complexity_level': scenario['complexity'],
                'expected_answer_type': 'detailed',
                'domain_category': scenario['domain']
            }
        )
        
        # Add evaluation metrics
        metrics = {
            'faithfulness_score': 0.8 + (i * 0.05),
            'answer_relevancy_score': 0.85 + (i * 0.03),
            'context_precision_score': 0.82 + (i * 0.04),
            'context_recall_score': 0.78 + (i * 0.06),
            'chunks_retrieved_count': scenario['chunks_count'],
            'chunks_expected_count': scenario['chunks_count'] - 1,
            'chunks_overlap_count': scenario['chunks_count'] - 1,
            'human_relevance_score': 4 + (i % 2),
            'human_accuracy_score': 4 + (i % 2)
        }
        
        capture.db.add_evaluation_metrics(
            response_id=result['response_id'],
            metrics=metrics,
            evaluation_method="test_data",
            evaluator="Test System"
        )
        
        print(f"✓ Created test scenario {i+1}: {scenario['question'][:50]}...")
    
    print(f"✓ Created comprehensive test dataset in session {capture.session_id}")
    return capture.session_id

def main():
    """Run all tests."""
    print("RAGAS Evaluation Database Test Suite")
    print("=" * 50)
    
    try:
        # Test basic database operations
        session_id_1 = test_database_creation()
        
        # Test chatbot integration
        session_id_2 = test_chatbot_integration()
        
        # Test data retrieval
        export_data = test_data_retrieval(session_id_2)
        
        # Create comprehensive test data
        session_id_3 = create_comprehensive_test_data()
        
        print(f"\n=== Test Summary ===")
        print(f"✓ All tests completed successfully!")
        print(f"✓ Created {3} test sessions:")
        print(f"  - Session {session_id_1}: Basic database operations")
        print(f"  - Session {session_id_2}: Chatbot integration")  
        print(f"  - Session {session_id_3}: Comprehensive test dataset")
        
        # Show database location
        db = RAGASEvaluationDB()
        print(f"✓ Database location: {db.db_path}")
        
        # List all sessions
        all_sessions = db.list_sessions()
        print(f"✓ Total sessions in database: {len(all_sessions)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
