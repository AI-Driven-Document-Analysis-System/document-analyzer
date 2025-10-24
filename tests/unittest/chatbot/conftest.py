"""
Pytest configuration and shared fixtures for chatbot tests
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return """
    Artificial Intelligence (AI) is transforming the world. Machine learning, 
    a subset of AI, enables computers to learn from data. Deep learning uses 
    neural networks with multiple layers to process complex patterns.
    """


@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "What is machine learning?"


@pytest.fixture
def mock_document_metadata():
    """Mock document metadata"""
    return {
        'document_id': 'doc_123',
        'filename': 'test_document.pdf',
        'type': 'research paper',
        'page_count': 10,
        'upload_date': '2024-01-01'
    }
