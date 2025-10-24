"""
Unit tests for Surya Document Processor
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path


class TestSuryaDocumentProcessor:
    """Test suite for Surya Document Processor"""
    
    @pytest.fixture
    def mock_surya_models(self):
        """Mock Surya models"""
        with patch('app.services.layout_analysis.surya_processor.load_model') as mock_load, \
             patch('app.services.layout_analysis.surya_processor.load_processor') as mock_proc:
            mock_load.return_value = Mock()
            mock_proc.return_value = Mock()
            yield mock_load, mock_proc
    
    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a sample PDF file path"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4 fake pdf content')
        return str(pdf_file)
    
    @pytest.fixture
    def sample_image_path(self, tmp_path):
        """Create a sample image file path"""
        img_file = tmp_path / "test.png"
        img_file.write_bytes(b'\x89PNG fake image content')
        return str(img_file)
    
    def test_initialization_default(self, mock_surya_models):
        """Test processor initialization with default settings"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        processor = SuryaDocumentProcessor()
        
        assert processor.preprocess_scanned is False
    
    def test_initialization_with_preprocessing(self, mock_surya_models):
        """Test processor initialization with preprocessing enabled"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        processor = SuryaDocumentProcessor(preprocess_scanned=True)
        
        assert processor.preprocess_scanned is True
    
    @patch('app.services.layout_analysis.surya_processor.load_model')
    @patch('app.services.layout_analysis.surya_processor.load_processor')
    def test_model_loading(self, mock_proc, mock_load):
        """Test that models are loaded during initialization"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        processor = SuryaDocumentProcessor()
        
        # Verify models were loaded
        assert mock_load.called
        assert mock_proc.called
    
    def test_pdf_conversion_to_images(self, mock_surya_models, sample_pdf_path):
        """Test PDF to image conversion"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        with patch('app.services.layout_analysis.surya_processor.convert_from_path') as mock_convert:
            mock_convert.return_value = [Mock(), Mock()]  # 2 pages
            
            processor = SuryaDocumentProcessor()
            images = processor._pdf_to_images(sample_pdf_path)
            
            assert len(images) == 2
            mock_convert.assert_called_once()
    
    def test_image_preprocessing(self, mock_surya_models):
        """Test image preprocessing for scanned documents"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        import numpy as np
        
        processor = SuryaDocumentProcessor(preprocess_scanned=True)
        
        # Create a mock image
        mock_image = Image.new('RGB', (100, 100), color='white')
        
        with patch.object(processor, '_preprocess_image') as mock_preprocess:
            mock_preprocess.return_value = mock_image
            result = processor._preprocess_image(mock_image)
            
            assert result is not None
            mock_preprocess.assert_called_once()
    
    def test_text_extraction_from_image(self, mock_surya_models):
        """Test text extraction from image"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        mock_image = Image.new('RGB', (100, 100))
        
        with patch.object(processor, '_extract_text_from_image') as mock_extract:
            mock_extract.return_value = {
                'text': 'Extracted text',
                'confidence': 0.95,
                'layout': []
            }
            
            result = processor._extract_text_from_image(mock_image)
            
            assert result['text'] == 'Extracted text'
            assert result['confidence'] == 0.95
    
    def test_layout_detection(self, mock_surya_models):
        """Test layout detection in document"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        mock_image = Image.new('RGB', (100, 100))
        
        with patch.object(processor, '_detect_layout') as mock_detect:
            mock_detect.return_value = [
                {'type': 'text', 'bbox': [10, 10, 90, 30]},
                {'type': 'image', 'bbox': [10, 40, 90, 80]}
            ]
            
            layout = processor._detect_layout(mock_image)
            
            assert len(layout) == 2
            assert layout[0]['type'] == 'text'
            assert layout[1]['type'] == 'image'
    
    def test_process_single_page_pdf(self, mock_surya_models, sample_pdf_path):
        """Test processing single page PDF"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100))]
            mock_extract.return_value = {
                'text': 'Page 1 text',
                'confidence': 0.92,
                'layout': []
            }
            
            result = processor.process_document(sample_pdf_path)
            
            assert 'extracted_text' in result
            assert result['page_count'] == 1
    
    def test_process_multipage_pdf(self, mock_surya_models, sample_pdf_path):
        """Test processing multi-page PDF"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [
                Image.new('RGB', (100, 100)),
                Image.new('RGB', (100, 100)),
                Image.new('RGB', (100, 100))
            ]
            mock_extract.side_effect = [
                {'text': 'Page 1', 'confidence': 0.9, 'layout': []},
                {'text': 'Page 2', 'confidence': 0.91, 'layout': []},
                {'text': 'Page 3', 'confidence': 0.89, 'layout': []}
            ]
            
            result = processor.process_document(sample_pdf_path)
            
            assert result['page_count'] == 3
            assert 'Page 1' in result['extracted_text']
            assert 'Page 2' in result['extracted_text']
            assert 'Page 3' in result['extracted_text']
    
    def test_process_image_file(self, mock_surya_models, sample_image_path):
        """Test processing image file directly"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        processor = SuryaDocumentProcessor()
        
        with patch('PIL.Image.open') as mock_open, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_open.return_value = Mock()
            mock_extract.return_value = {
                'text': 'Image text',
                'confidence': 0.88,
                'layout': []
            }
            
            result = processor.process_document(sample_image_path)
            
            assert result['extracted_text'] == 'Image text'
            assert result['page_count'] == 1
    
    def test_confidence_calculation(self, mock_surya_models, sample_pdf_path):
        """Test average confidence calculation"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100)) for _ in range(3)]
            mock_extract.side_effect = [
                {'text': 'P1', 'confidence': 0.9, 'layout': []},
                {'text': 'P2', 'confidence': 0.8, 'layout': []},
                {'text': 'P3', 'confidence': 0.7, 'layout': []}
            ]
            
            result = processor.process_document(sample_pdf_path)
            
            # Average should be (0.9 + 0.8 + 0.7) / 3 = 0.8
            assert abs(result['confidence'] - 0.8) < 0.01
    
    def test_empty_page_handling(self, mock_surya_models, sample_pdf_path):
        """Test handling of empty pages"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100))]
            mock_extract.return_value = {
                'text': '',
                'confidence': 0.0,
                'layout': []
            }
            
            result = processor.process_document(sample_pdf_path)
            
            assert result['extracted_text'] == ''
            assert result['page_count'] == 1
    
    def test_error_handling_corrupted_pdf(self, mock_surya_models, sample_pdf_path):
        """Test error handling for corrupted PDF"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf:
            mock_pdf.side_effect = Exception("Corrupted PDF")
            
            with pytest.raises(Exception):
                processor.process_document(sample_pdf_path)
    
    def test_layout_element_types(self, mock_surya_models, sample_pdf_path):
        """Test detection of different layout element types"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100))]
            mock_extract.return_value = {
                'text': 'Text',
                'confidence': 0.9,
                'layout': [
                    {'type': 'heading', 'bbox': [0, 0, 100, 20]},
                    {'type': 'paragraph', 'bbox': [0, 25, 100, 60]},
                    {'type': 'table', 'bbox': [0, 65, 100, 95]},
                    {'type': 'image', 'bbox': [0, 100, 50, 150]}
                ]
            }
            
            result = processor.process_document(sample_pdf_path)
            
            assert len(result['layout_elements']) == 4
            types = [elem['type'] for elem in result['layout_elements']]
            assert 'heading' in types
            assert 'paragraph' in types
            assert 'table' in types
            assert 'image' in types
    
    def test_bbox_coordinates(self, mock_surya_models, sample_pdf_path):
        """Test bounding box coordinates are preserved"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100))]
            mock_extract.return_value = {
                'text': 'Text',
                'confidence': 0.9,
                'layout': [
                    {'type': 'text', 'bbox': [10, 20, 90, 40]}
                ]
            }
            
            result = processor.process_document(sample_pdf_path)
            
            bbox = result['layout_elements'][0]['bbox']
            assert bbox == [10, 20, 90, 40]
    
    def test_document_with_tables(self, mock_surya_models, sample_pdf_path):
        """Test processing document with tables"""
        from app.services.layout_analysis.surya_processor import SuryaDocumentProcessor
        from PIL import Image
        
        processor = SuryaDocumentProcessor()
        
        with patch.object(processor, '_pdf_to_images') as mock_pdf, \
             patch.object(processor, '_extract_text_from_image') as mock_extract:
            
            mock_pdf.return_value = [Image.new('RGB', (100, 100))]
            mock_extract.return_value = {
                'text': 'Table data: Row1 Col1, Row1 Col2',
                'confidence': 0.85,
                'layout': [
                    {'type': 'table', 'bbox': [0, 0, 100, 100], 'rows': 2, 'cols': 2}
                ]
            }
            
            result = processor.process_document(sample_pdf_path)
            
            table_elements = [e for e in result['layout_elements'] if e['type'] == 'table']
            assert len(table_elements) == 1
            assert table_elements[0]['rows'] == 2
            assert table_elements[0]['cols'] == 2
