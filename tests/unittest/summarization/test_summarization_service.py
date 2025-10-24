"""
Unit tests for Summarization Service
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.summarization_service import (
    get_summary_options,
    _get_model_endpoint,
    _select_optimal_model,
    _get_model_specific_parameters,
    summarize_with_options
)


class TestSummarizationService:
    """Test suite for Summarization Service"""
    
    def test_get_summary_options(self):
        """Test getting available summary options"""
        options = get_summary_options()
        
        assert "brief" in options
        assert "detailed" in options
        assert "domain_specific" in options
        
        # Check brief summary config
        assert options["brief"]["name"] == "Brief Summary"
        assert options["brief"]["model"] == "pegasus"
        assert options["brief"]["max_length"] > 0
        assert options["brief"]["min_length"] > 0
        
        # Check detailed summary config
        assert options["detailed"]["name"] == "Detailed Summary"
        assert options["detailed"]["model"] == "bart"
        
        # Check domain specific config
        assert options["domain_specific"]["name"] == "Domain Specific Summary"
    
    def test_get_model_endpoint_bart(self):
        """Test getting BART model endpoint"""
        endpoint = _get_model_endpoint("bart")
        
        assert "huggingface.co" in endpoint
        assert "facebook/bart-large-cnn" in endpoint
    
    def test_get_model_endpoint_pegasus(self):
        """Test getting Pegasus model endpoint"""
        endpoint = _get_model_endpoint("pegasus")
        
        assert "huggingface.co" in endpoint
        assert "google/pegasus" in endpoint
    
    def test_get_model_endpoint_t5(self):
        """Test getting T5 model endpoint"""
        endpoint = _get_model_endpoint("t5")
        
        assert "huggingface.co" in endpoint
        assert "flan-t5" in endpoint
    
    def test_get_model_endpoint_invalid(self):
        """Test getting endpoint for invalid model"""
        with pytest.raises(ValueError):
            _get_model_endpoint("invalid_model")
    
    def test_select_optimal_model_domain_specific(self):
        """Test model selection for domain-specific summaries"""
        text = "Sample text " * 100
        model = _select_optimal_model(text, "Domain Specific Summary", "medical", "t5")
        
        # Should always use BART for domain-specific
        assert model == "bart"
    
    def test_select_optimal_model_long_document(self):
        """Test model selection for long documents"""
        text = "word " * 2500  # >2000 words
        model = _select_optimal_model(text, "Detailed Summary", "general", "pegasus")
        
        # Should use BART for long documents
        assert model == "bart"
    
    def test_select_optimal_model_brief(self):
        """Test model selection for brief summaries"""
        text = "Sample text " * 100
        model = _select_optimal_model(text, "Brief Summary", "general", "pegasus")
        
        # Should keep original model for brief
        assert model == "pegasus"
    
    def test_select_optimal_model_detailed(self):
        """Test model selection for detailed summaries"""
        text = "Sample text " * 100
        model = _select_optimal_model(text, "Detailed Summary", "general", "bart")
        
        # Should keep original model for detailed
        assert model == "bart"
    
    def test_get_model_specific_parameters_bart(self):
        """Test BART-specific parameters"""
        base_params = {"max_length": 150, "min_length": 50}
        params = _get_model_specific_parameters("bart", base_params)
        
        assert "do_sample" in params
        assert "num_beams" in params
        assert params["max_length"] == 150
        assert params["min_length"] == 50
    
    def test_get_model_specific_parameters_pegasus(self):
        """Test Pegasus-specific parameters"""
        base_params = {"max_length": 150, "min_length": 50}
        params = _get_model_specific_parameters("pegasus", base_params)
        
        assert "max_length" in params
        assert "min_length" in params
    
    def test_get_model_specific_parameters_t5(self):
        """Test T5-specific parameters"""
        base_params = {"max_length": 150, "min_length": 50}
        params = _get_model_specific_parameters("t5", base_params)
        
        assert "max_length" in params
        assert "min_length" in params
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_with_options_success(self, mock_post):
        """Test successful summarization"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "summary_text": "This is a test summary."
        }]
        mock_post.return_value = mock_response
        
        text = "This is a long document that needs to be summarized. " * 20
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        result = summarize_with_options(text, options)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_with_options_api_error(self, mock_post):
        """Test summarization with API error"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service unavailable"
        mock_post.return_value = mock_response
        
        text = "Sample text " * 50
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        # Should handle error gracefully
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_empty_text(self, mock_post):
        """Test summarization with empty text"""
        text = ""
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        result = summarize_with_options(text, options)
        
        # Should handle empty text
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_very_short_text(self, mock_post):
        """Test summarization with very short text"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "summary_text": "Short summary."
        }]
        mock_post.return_value = mock_response
        
        text = "This is short."
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_with_cancellation_token(self, mock_post):
        """Test summarization with cancellation token"""
        from threading import Event
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "summary_text": "Summary text."
        }]
        mock_post.return_value = mock_response
        
        text = "Sample text " * 50
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        cancellation_token = Event()
        
        result = summarize_with_options(text, options, cancellation_token)
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_cancelled_request(self, mock_post):
        """Test summarization with cancelled request"""
        from threading import Event
        
        text = "Sample text " * 50
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        cancellation_token = Event()
        cancellation_token.set()  # Cancel immediately
        
        # Should detect cancellation
        result = summarize_with_options(text, options, cancellation_token)
        assert isinstance(result, str)
    
    def test_summary_options_length_constraints(self):
        """Test that summary options have valid length constraints"""
        options = get_summary_options()
        
        for option_type, config in options.items():
            assert config["max_length"] > config["min_length"]
            assert config["min_length"] > 0
            assert config["max_length"] < 1000  # Reasonable upper bound
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_special_characters(self, mock_post):
        """Test summarization with special characters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "summary_text": "Summary with émojis 🚀"
        }]
        mock_post.return_value = mock_response
        
        text = "Text with émojis 🚀 and symbols @#$% " * 20
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_multiline_text(self, mock_post):
        """Test summarization with multiline text"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "summary_text": "Multiline summary."
        }]
        mock_post.return_value = mock_response
        
        text = "Line 1\nLine 2\nLine 3\n" * 20
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
    
    def test_model_endpoint_consistency(self):
        """Test that model endpoints are consistent"""
        models = ["bart", "pegasus", "t5"]
        
        for model in models:
            endpoint = _get_model_endpoint(model)
            assert endpoint.startswith("https://")
            assert "huggingface.co" in endpoint
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_timeout_handling(self, mock_post):
        """Test handling of request timeouts"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        text = "Sample text " * 50
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        # Should handle timeout gracefully
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
    
    @patch('app.services.summarization_service.requests.post')
    def test_summarize_connection_error(self, mock_post):
        """Test handling of connection errors"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        text = "Sample text " * 50
        options = {
            "model": "bart",
            "name": "Brief Summary",
            "max_length": 150,
            "min_length": 50
        }
        
        # Should handle connection error gracefully
        result = summarize_with_options(text, options)
        assert isinstance(result, str)
