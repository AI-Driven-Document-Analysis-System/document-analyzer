"""
Pytest configuration and shared fixtures for OCR tests
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import io

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF file bytes"""
    return b'%PDF-1.4\n%fake pdf content for testing'


@pytest.fixture
def sample_image():
    """Create a sample PIL Image"""
    return Image.new('RGB', (200, 100), color='white')


@pytest.fixture
def sample_image_bytes():
    """Sample image file bytes"""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def mock_ocr_result():
    """Mock OCR processing result"""
    return {
        'extracted_text': 'This is sample extracted text from a document.',
        'layout_elements': [
            {
                'type': 'heading',
                'content': 'Document Title',
                'bbox': [50, 50, 500, 100],
                'confidence': 0.95
            },
            {
                'type': 'paragraph',
                'content': 'This is a paragraph of text.',
                'bbox': [50, 120, 500, 200],
                'confidence': 0.92
            }
        ],
        'page_count': 1,
        'confidence': 0.93,
        'processing_time': 1.5
    }


@pytest.fixture
def mock_multipage_result():
    """Mock multi-page OCR result"""
    return {
        'extracted_text': 'Page 1 text\n\nPage 2 text\n\nPage 3 text',
        'layout_elements': [],
        'page_count': 3,
        'confidence': 0.88,
        'processing_time': 4.2
    }


@pytest.fixture
def sample_layout_elements():
    """Sample layout elements"""
    return [
        {'type': 'heading', 'bbox': [0, 0, 200, 30], 'content': 'Title'},
        {'type': 'paragraph', 'bbox': [0, 40, 200, 100], 'content': 'Body text'},
        {'type': 'table', 'bbox': [0, 110, 200, 200], 'content': 'Table data'},
        {'type': 'image', 'bbox': [0, 210, 200, 300], 'content': 'Image'}
    ]
