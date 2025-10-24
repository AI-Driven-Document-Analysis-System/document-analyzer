"""
Pytest configuration and shared fixtures for summarization tests
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_text_short():
    """Short sample text for testing"""
    return "This is a short document with minimal content for testing purposes."


@pytest.fixture
def sample_text_medium():
    """Medium length sample text"""
    return """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the 
    natural intelligence displayed by humans and animals. Leading AI textbooks define the field 
    as the study of "intelligent agents": any device that perceives its environment and takes 
    actions that maximize its chance of successfully achieving its goals. Colloquially, the term 
    "artificial intelligence" is often used to describe machines that mimic "cognitive" functions 
    that humans associate with the human mind, such as "learning" and "problem solving".
    """ * 5


@pytest.fixture
def sample_text_long():
    """Long sample text for testing"""
    return """
    Machine learning is a method of data analysis that automates analytical model building. 
    It is a branch of artificial intelligence based on the idea that systems can learn from data, 
    identify patterns and make decisions with minimal human intervention. Machine learning algorithms 
    are used in a wide variety of applications, such as email filtering and computer vision, where 
    it is difficult or unfeasible to develop conventional algorithms to perform the needed tasks.
    """ * 100


@pytest.fixture
def mock_summary_response():
    """Mock API response for summarization"""
    return [{
        "summary_text": "This is a generated summary of the document content."
    }]


@pytest.fixture
def summary_options_brief():
    """Brief summary options"""
    return {
        "model": "pegasus",
        "name": "Brief Summary",
        "max_length": 150,
        "min_length": 50
    }


@pytest.fixture
def summary_options_detailed():
    """Detailed summary options"""
    return {
        "model": "bart",
        "name": "Detailed Summary",
        "max_length": 400,
        "min_length": 150
    }


@pytest.fixture
def summary_options_domain_specific():
    """Domain-specific summary options"""
    return {
        "model": "t5",
        "name": "Domain Specific Summary",
        "max_length": 350,
        "min_length": 120
    }
