"""
Pytest configuration and shared fixtures for classification tests
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_classification_result():
    """Mock classification result"""
    return (
        "research paper",
        {
            "research paper": 0.95,
            "legal docs": 0.03,
            "invoices": 0.01,
            "medical report": 0.01
        }
    )


@pytest.fixture
def document_types():
    """List of supported document types"""
    return [
        "research paper",
        "legal docs",
        "invoices",
        "medical report",
        "letters",
        "financial docs",
        "news"
    ]


@pytest.fixture
def sample_confidence_scores():
    """Sample confidence scores for different document types"""
    return {
        "high_confidence": {
            "research paper": 0.95,
            "legal docs": 0.03,
            "invoices": 0.02
        },
        "medium_confidence": {
            "research paper": 0.65,
            "legal docs": 0.25,
            "invoices": 0.10
        },
        "low_confidence": {
            "research paper": 0.35,
            "legal docs": 0.33,
            "invoices": 0.32
        }
    }
