"""
Unit tests for Document Classification Service
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import asyncio
from app.services.classifcation.classification import DocumentClassifier


class TestDocumentClassifier:
    """Test suite for DocumentClassifier class"""
    
    @pytest.fixture
    def classifier(self):
        """Create a DocumentClassifier instance"""
        return DocumentClassifier()
    
    @pytest.fixture
    def mock_gradio_client(self):
        """Create a mock Gradio client"""
        client = Mock()
        client.predict = Mock(return_value=(
            "research paper",
            {"research paper": 0.95, "legal docs": 0.03, "invoices": 0.02},
            None  # image
        ))
        return client
    
    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier.space_name == "RavindiG/document_classification"
        assert classifier.client is None
    
    @patch('app.services.classifcation.classification.Client')
    def test_initialize_sync_client_success(self, mock_client_class, classifier):
        """Test successful client initialization"""
        mock_client_class.return_value = Mock()
        
        result = classifier.initialize_sync_client()
        
        assert result is True
        assert classifier.client is not None
        mock_client_class.assert_called_once_with(classifier.space_name)
    
    @patch('app.services.classifcation.classification.Client')
    def test_initialize_sync_client_failure(self, mock_client_class, classifier):
        """Test client initialization failure"""
        mock_client_class.side_effect = Exception("Connection failed")
        
        result = classifier.initialize_sync_client()
        
        assert result is False
        assert classifier.client is None
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_document_file_not_found(self, mock_exists, classifier):
        """Test classification with non-existent file"""
        mock_exists.return_value = False
        
        result = await classifier.classify_document("nonexistent.pdf")
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_document_success(self, mock_exists, classifier, mock_gradio_client, tmp_path):
        """Test successful document classification"""
        # Create a temporary file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        mock_exists.return_value = True
        classifier.client = mock_gradio_client
        
        result = await classifier.classify_document(str(test_file))
        
        assert result is not None
        assert len(result) == 2
        doc_type, confidence = result
        assert doc_type == "research paper"
        assert isinstance(confidence, dict)
        assert confidence["research paper"] == 0.95
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_document_api_error(self, mock_exists, classifier, tmp_path):
        """Test classification with API error"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client.predict.side_effect = Exception("API Error")
        classifier.client = mock_client
        
        result = await classifier.classify_document(str(test_file))
        
        assert result is None
    
    def test_call_gradio_predict_method1_success(self, classifier, mock_gradio_client, tmp_path):
        """Test Gradio predict with method 1 (handle_file)"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        classifier.client = mock_gradio_client
        
        result = classifier._call_gradio_predict(str(test_file))
        
        assert result is not None
        assert result[0] == "research paper"
    
    def test_call_gradio_predict_no_client(self, classifier, tmp_path):
        """Test Gradio predict without initialized client"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        with patch.object(classifier, 'initialize_sync_client', return_value=False):
            result = classifier._call_gradio_predict(str(test_file))
        
        assert result is None
    
    def test_call_gradio_predict_method_fallback(self, classifier, tmp_path):
        """Test Gradio predict with method fallback"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        mock_client = Mock()
        # Method 1 fails
        mock_client.predict.side_effect = [
            Exception("Method 1 failed"),
            ("legal docs", {"legal docs": 0.88}, None)  # Method 2 succeeds
        ]
        classifier.client = mock_client
        
        result = classifier._call_gradio_predict(str(test_file))
        
        assert result is not None
        assert result[0] == "legal docs"
    
    def test_call_gradio_predict_all_methods_fail(self, classifier, tmp_path):
        """Test when all prediction methods fail"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        mock_client = Mock()
        mock_client.predict.side_effect = Exception("All methods failed")
        classifier.client = mock_client
        
        result = classifier._call_gradio_predict(str(test_file))
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_different_document_types(self, mock_exists, classifier, tmp_path):
        """Test classification of different document types"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        mock_exists.return_value = True
        
        document_types = [
            ("research paper", {"research paper": 0.95}),
            ("legal docs", {"legal docs": 0.90}),
            ("invoices", {"invoices": 0.85}),
            ("medical report", {"medical report": 0.92}),
            ("letters", {"letters": 0.88})
        ]
        
        for doc_type, confidence in document_types:
            mock_client = Mock()
            mock_client.predict.return_value = (doc_type, confidence, None)
            classifier.client = mock_client
            
            result = await classifier.classify_document(str(test_file))
            
            assert result is not None
            assert result[0] == doc_type
            assert result[1] == confidence
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_low_confidence(self, mock_exists, classifier, mock_gradio_client, tmp_path):
        """Test classification with low confidence scores"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        mock_exists.return_value = True
        
        mock_client = Mock()
        mock_client.predict.return_value = (
            "unknown",
            {"research paper": 0.35, "legal docs": 0.33, "invoices": 0.32},
            None
        )
        classifier.client = mock_client
        
        result = await classifier.classify_document(str(test_file))
        
        assert result is not None
        # Should still return result even with low confidence
        assert result[0] == "unknown"
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_multiple_documents(self, mock_exists, classifier, tmp_path):
        """Test classifying multiple documents sequentially"""
        mock_exists.return_value = True
        
        files = []
        for i in range(3):
            test_file = tmp_path / f"test{i}.pdf"
            test_file.write_bytes(b'fake pdf content')
            files.append(str(test_file))
        
        mock_client = Mock()
        mock_client.predict.side_effect = [
            ("research paper", {"research paper": 0.95}, None),
            ("legal docs", {"legal docs": 0.90}, None),
            ("invoices", {"invoices": 0.85}, None)
        ]
        classifier.client = mock_client
        
        results = []
        for file_path in files:
            result = await classifier.classify_document(file_path)
            results.append(result)
        
        assert len(results) == 3
        assert all(r is not None for r in results)
        assert results[0][0] == "research paper"
        assert results[1][0] == "legal docs"
        assert results[2][0] == "invoices"
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_with_image_file(self, mock_exists, classifier, tmp_path):
        """Test classification with image file"""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b'fake image content')
        mock_exists.return_value = True
        
        mock_client = Mock()
        mock_client.predict.return_value = (
            "research paper",
            {"research paper": 0.88},
            None
        )
        classifier.client = mock_client
        
        result = await classifier.classify_document(str(test_file))
        
        assert result is not None
        assert result[0] == "research paper"
    
    def test_confidence_scores_structure(self, classifier, mock_gradio_client, tmp_path):
        """Test that confidence scores have correct structure"""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'fake pdf content')
        
        classifier.client = mock_gradio_client
        result = classifier._call_gradio_predict(str(test_file))
        
        assert result is not None
        confidence = result[1]
        assert isinstance(confidence, dict)
        assert all(isinstance(k, str) for k in confidence.keys())
        assert all(isinstance(v, (int, float)) for v in confidence.values())
        assert all(0 <= v <= 1 for v in confidence.values())
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_empty_file(self, mock_exists, classifier, tmp_path):
        """Test classification with empty file"""
        test_file = tmp_path / "empty.pdf"
        test_file.write_bytes(b'')
        mock_exists.return_value = True
        
        mock_client = Mock()
        mock_client.predict.side_effect = Exception("Empty file")
        classifier.client = mock_client
        
        result = await classifier.classify_document(str(test_file))
        
        # Should handle empty file gracefully
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.classifcation.classification.os.path.exists')
    async def test_classify_corrupted_file(self, mock_exists, classifier, tmp_path):
        """Test classification with corrupted file"""
        test_file = tmp_path / "corrupted.pdf"
        test_file.write_bytes(b'corrupted content')
        mock_exists.return_value = True
        
        mock_client = Mock()
        mock_client.predict.side_effect = Exception("Corrupted file")
        classifier.client = mock_client
        
        result = await classifier.classify_document(str(test_file))
        
        assert result is None
