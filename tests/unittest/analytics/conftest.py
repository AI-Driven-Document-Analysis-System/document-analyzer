"""
Pytest configuration and shared fixtures for analytics tests
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_upload_data():
    """Mock document upload data"""
    return [
        {
            "date": (datetime.now() - timedelta(days=i)).date(),
            "uploads": 5 + i,
            "totalSize": 1024000 * (i + 1)
        }
        for i in range(7)
    ]


@pytest.fixture
def mock_document_types():
    """Mock document types distribution"""
    return [
        {"type": "research paper", "count": 25, "avgSize": 512000},
        {"type": "legal docs", "count": 15, "avgSize": 1024000},
        {"type": "invoices", "count": 10, "avgSize": 256000},
        {"type": "medical report", "count": 8, "avgSize": 768000},
        {"type": "letters", "count": 5, "avgSize": 128000}
    ]


@pytest.fixture
def mock_ocr_scores():
    """Mock OCR confidence scores"""
    return [0.45, 0.62, 0.78, 0.85, 0.92, 0.96, 0.88, 0.73, 0.95, 0.81]


@pytest.fixture
def mock_model_usage():
    """Mock model usage data"""
    return {
        "bart": [
            {"date": "2024-01-01", "count": 10},
            {"date": "2024-01-02", "count": 15}
        ],
        "pegasus": [
            {"date": "2024-01-01", "count": 5},
            {"date": "2024-01-02", "count": 8}
        ],
        "t5": [
            {"date": "2024-01-01", "count": 3},
            {"date": "2024-01-02", "count": 4}
        ]
    }


@pytest.fixture
def mock_chat_distribution():
    """Mock chat distribution data"""
    return [
        {"day": "01", "full_date": "2024-01-01", "count": 10},
        {"day": "02", "full_date": "2024-01-02", "count": 15},
        {"day": "03", "full_date": "2024-01-03", "count": 8},
        {"day": "04", "full_date": "2024-01-04", "count": 12}
    ]


@pytest.fixture
def mock_upload_trends():
    """Mock upload trends data"""
    return {
        "byDayOfWeek": [
            {"day": "Monday", "count": 10},
            {"day": "Tuesday", "count": 15},
            {"day": "Wednesday", "count": 12},
            {"day": "Thursday", "count": 18},
            {"day": "Friday", "count": 20}
        ],
        "byHourOfDay": [
            {"hour": "09:00", "count": 5},
            {"hour": "10:00", "count": 8},
            {"hour": "14:00", "count": 12},
            {"hour": "15:00", "count": 10}
        ]
    }


@pytest.fixture
def storage_limits():
    """Storage limit constants"""
    return {
        "total": 300 * 1024 * 1024,  # 300MB
        "warning_threshold": 0.8,     # 80%
        "critical_threshold": 0.95    # 95%
    }
