"""
Unit tests for OCR Service
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from app.services.ocr_service_surya import OCRService, OCRProvider


class TestOCRService:
    """Test suite for OCRService class"""
    
    @pytest.fixture
    def mock_surya_processor(self):
        """Create a mock Surya processor"""
        processor = Mock()
        processor.process_document = Mock(return_value={
            'extracted_text': 'Sample extracted text from Surya',
            'layout_elements': [
                {'type': 'text', 'content': 'Sample text', 'bbox': [0, 0, 100, 100]}
            ],
            'page_count': 1,
            'confidence': 0.95
        })
        return processor
    
    @pytest.fixture
    def mock_aws_service(self):
        """Create a mock AWS Textract service"""
        service = Mock()
        service.process_document = Mock(return_value={
            'extracted_text': 'Sample extracted text from AWS',
            'layout_elements': [],
            'page_count': 1,
            'confidence': 0.98
        })
        return service
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_initialization_surya(self, mock_surya_class):
        """Test OCR service initialization with Surya"""
        mock_surya_class.return_value = Mock()
        
        service = OCRService(provider=OCRProvider.SURYA)
        
        assert service.provider == OCRProvider.SURYA
        assert service.surya_service is not None
        mock_surya_class.assert_called_once()
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_initialization_default_provider(self, mock_surya_class):
        """Test default provider is Surya"""
        mock_surya_class.return_value = Mock()
        
        service = OCRService()
        
        assert service.provider == OCRProvider.SURYA
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    @patch('app.services.ocr_service_surya.AWSTextractService')
    def test_surya_initialization_failure_fallback(self, mock_aws_class, mock_surya_class):
        """Test fallback to AWS when Surya initialization fails"""
        mock_surya_class.side_effect = Exception("Surya init failed")
        mock_aws_class.return_value = Mock()
        
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret'
        }):
            service = OCRService()
        
        assert service.provider == OCRProvider.AWS_TEXTRACT
        assert service.aws_service is not None
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_document_with_surya(self, mock_surya_class, mock_surya_processor):
        """Test document processing with Surya"""
        mock_surya_class.return_value = mock_surya_processor
        
        service = OCRService()
        result = service.process_document('test.pdf', 'doc_123')
        
        assert 'extracted_text' in result
        assert result['extracted_text'] == 'Sample extracted text from Surya'
        assert 'layout_elements' in result
        assert result['page_count'] == 1
        mock_surya_processor.process_document.assert_called_once_with('test.pdf', 'doc_123')
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_document_without_document_id(self, mock_surya_class, mock_surya_processor):
        """Test processing document without document ID"""
        mock_surya_class.return_value = mock_surya_processor
        
        service = OCRService()
        result = service.process_document('test.pdf')
        
        assert result is not None
        mock_surya_processor.process_document.assert_called_once()
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    @patch('app.services.ocr_service_surya.AWSTextractService')
    def test_fallback_to_aws_on_surya_failure(self, mock_aws_class, mock_surya_class):
        """Test fallback to AWS when Surya processing fails"""
        mock_surya = Mock()
        mock_surya.process_document.side_effect = Exception("Surya processing failed")
        mock_surya_class.return_value = mock_surya
        
        mock_aws = Mock()
        mock_aws.process_document.return_value = {
            'extracted_text': 'AWS fallback text',
            'page_count': 1
        }
        mock_aws_class.return_value = mock_aws
        
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret'
        }):
            service = OCRService()
            service.aws_service = mock_aws
            
            result = service.process_document('test.pdf', 'doc_123')
        
        assert result['extracted_text'] == 'AWS fallback text'
        mock_aws.process_document.assert_called_once()
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_multipage_document(self, mock_surya_class):
        """Test processing multi-page document"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Page 1 text\nPage 2 text\nPage 3 text',
            'layout_elements': [],
            'page_count': 3,
            'confidence': 0.92
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('multipage.pdf', 'doc_456')
        
        assert result['page_count'] == 3
        assert 'Page 1' in result['extracted_text']
        assert 'Page 3' in result['extracted_text']
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_image_file(self, mock_surya_class, mock_surya_processor):
        """Test processing image file"""
        mock_surya_class.return_value = mock_surya_processor
        
        service = OCRService()
        result = service.process_document('image.png', 'doc_789')
        
        assert result is not None
        assert 'extracted_text' in result
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_layout_elements_extraction(self, mock_surya_class):
        """Test extraction of layout elements"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Document text',
            'layout_elements': [
                {'type': 'heading', 'content': 'Title', 'bbox': [0, 0, 200, 50]},
                {'type': 'paragraph', 'content': 'Body text', 'bbox': [0, 60, 200, 150]},
                {'type': 'table', 'content': 'Table data', 'bbox': [0, 160, 200, 300]}
            ],
            'page_count': 1
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('document.pdf')
        
        assert len(result['layout_elements']) == 3
        assert result['layout_elements'][0]['type'] == 'heading'
        assert result['layout_elements'][1]['type'] == 'paragraph'
        assert result['layout_elements'][2]['type'] == 'table'
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_confidence_score(self, mock_surya_class):
        """Test OCR confidence score"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Text',
            'layout_elements': [],
            'page_count': 1,
            'confidence': 0.87
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('test.pdf')
        
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1
        assert result['confidence'] == 0.87
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_empty_document(self, mock_surya_class):
        """Test processing empty document"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': '',
            'layout_elements': [],
            'page_count': 0,
            'confidence': 0.0
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('empty.pdf')
        
        assert result['extracted_text'] == ''
        assert result['page_count'] == 0
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_special_characters_handling(self, mock_surya_class):
        """Test handling of special characters in OCR"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Text with émojis 🚀 and symbols: @#$%',
            'layout_elements': [],
            'page_count': 1,
            'confidence': 0.90
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('special_chars.pdf')
        
        assert '🚀' in result['extracted_text']
        assert '@#$%' in result['extracted_text']
        assert 'émojis' in result['extracted_text']
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_large_document_processing(self, mock_surya_class):
        """Test processing large document"""
        mock_surya = Mock()
        large_text = 'A' * 100000  # 100k characters
        mock_surya.process_document.return_value = {
            'extracted_text': large_text,
            'layout_elements': [],
            'page_count': 50,
            'confidence': 0.88
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('large_doc.pdf')
        
        assert len(result['extracted_text']) == 100000
        assert result['page_count'] == 50
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_provider_enum(self, mock_surya_class):
        """Test OCRProvider enum values"""
        mock_surya_class.return_value = Mock()
        
        assert OCRProvider.SURYA == "surya"
        assert OCRProvider.AWS_TEXTRACT == "aws_textract"
        
        service = OCRService(provider=OCRProvider.SURYA)
        assert service.provider == OCRProvider.SURYA
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_with_preprocessing(self, mock_surya_class):
        """Test Surya processor initialized with preprocessing enabled"""
        mock_surya_class.return_value = Mock()
        
        service = OCRService()
        
        # Verify Surya was initialized with preprocessing
        mock_surya_class.assert_called_once_with(preprocess_scanned=True)
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_process_scanned_document(self, mock_surya_class):
        """Test processing scanned document"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Scanned document text',
            'layout_elements': [],
            'page_count': 1,
            'confidence': 0.75,
            'is_scanned': True
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('scanned.pdf')
        
        assert result['is_scanned'] is True
        assert result['confidence'] == 0.75
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_error_handling_invalid_file(self, mock_surya_class):
        """Test error handling for invalid file"""
        mock_surya = Mock()
        mock_surya.process_document.side_effect = FileNotFoundError("File not found")
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        
        with pytest.raises(Exception):
            service.process_document('nonexistent.pdf')
    
    @patch('app.services.ocr_service_surya.SuryaDocumentProcessor')
    def test_metadata_extraction(self, mock_surya_class):
        """Test extraction of document metadata"""
        mock_surya = Mock()
        mock_surya.process_document.return_value = {
            'extracted_text': 'Text',
            'layout_elements': [],
            'page_count': 5,
            'confidence': 0.92,
            'metadata': {
                'author': 'Test Author',
                'creation_date': '2024-01-01',
                'language': 'en'
            }
        }
        mock_surya_class.return_value = mock_surya
        
        service = OCRService()
        result = service.process_document('doc_with_metadata.pdf')
        
        assert 'metadata' in result
        assert result['metadata']['author'] == 'Test Author'
        assert result['metadata']['language'] == 'en'
