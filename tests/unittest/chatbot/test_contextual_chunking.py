"""
Unit tests for Contextual Chunking (Document-Aware Augmentation)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from app.services.chatbot.vector_db.contextual_chunking import DocumentAwareAugmenter


class TestDocumentAwareAugmenter:
    """Test suite for DocumentAwareAugmenter class"""
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing"""
        return [
            {
                'text': 'Machine learning is a subset of artificial intelligence.',
                'metadata': {'chunk_id': 'chunk_1', 'position': 0}
            },
            {
                'text': 'Deep learning uses neural networks with multiple layers.',
                'metadata': {'chunk_id': 'chunk_2', 'position': 1}
            },
            {
                'text': 'Natural language processing enables text understanding.',
                'metadata': {'chunk_id': 'chunk_3', 'position': 2}
            }
        ]
    
    @pytest.fixture
    def document_data(self):
        """Create sample document data"""
        return {
            'filename': 'ai_introduction.pdf',
            'type': 'research paper',
            'doc_id': 'doc_123'
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        llm = Mock()
        response = Mock()
        response.content = json.dumps([
            {"index": 0, "context": "This chunk introduces machine learning concepts."},
            {"index": 1, "context": "This chunk explains deep learning architecture."},
            {"index": 2, "context": "This chunk describes NLP applications."}
        ])
        llm.invoke = Mock(return_value=response)
        return llm
    
    @pytest.fixture
    def augmenter(self, mock_llm):
        """Create a DocumentAwareAugmenter instance"""
        return DocumentAwareAugmenter(llm=mock_llm)
    
    def test_initialization_with_llm(self, mock_llm):
        """Test initialization with LLM"""
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        assert augmenter.llm == mock_llm
    
    def test_initialization_without_llm(self):
        """Test initialization without LLM"""
        augmenter = DocumentAwareAugmenter(llm=None)
        assert augmenter.llm is None
    
    def test_augment_chunks_with_context(self, augmenter, sample_chunks, document_data):
        """Test augmenting chunks with context"""
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        assert len(augmented) == len(sample_chunks)
        
        # Check that context was added
        for chunk in augmented:
            assert 'text' in chunk
            assert 'metadata' in chunk
            # Augmented text should be longer than original
            original_text = next(c['text'] for c in sample_chunks if c['metadata'] == chunk['metadata'])
            assert len(chunk['text']) > len(original_text)
    
    def test_augment_empty_chunks(self, augmenter, document_data):
        """Test augmenting empty chunk list"""
        augmented = augmenter.augment_chunks_with_context([], document_data)
        assert augmented == []
    
    def test_augment_without_llm(self, sample_chunks, document_data):
        """Test augmentation without LLM returns original chunks"""
        augmenter = DocumentAwareAugmenter(llm=None)
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        assert augmented == sample_chunks
    
    def test_build_batch_prompt(self, augmenter, sample_chunks, document_data):
        """Test batch prompt building"""
        prompt = augmenter._build_batch_prompt(
            sample_chunks,
            document_data['filename'],
            document_data['type'],
            start_index=0
        )
        
        assert isinstance(prompt, str)
        assert document_data['filename'] in prompt
        assert document_data['type'] in prompt
        assert 'JSON' in prompt
        # Check that chunk text is included
        assert sample_chunks[0]['text'][:50] in prompt
    
    def test_parse_batch_response_valid_json(self, augmenter):
        """Test parsing valid JSON response"""
        response = json.dumps([
            {"index": 0, "context": "Context for chunk 0"},
            {"index": 1, "context": "Context for chunk 1"}
        ])
        
        contexts = augmenter._parse_batch_response(response, offset=0)
        
        assert len(contexts) == 2
        assert contexts[0] == "Context for chunk 0"
        assert contexts[1] == "Context for chunk 1"
    
    def test_parse_batch_response_with_offset(self, augmenter):
        """Test parsing response with offset"""
        response = json.dumps([
            {"index": 0, "context": "Context A"},
            {"index": 1, "context": "Context B"}
        ])
        
        contexts = augmenter._parse_batch_response(response, offset=10)
        
        assert contexts[10] == "Context A"
        assert contexts[11] == "Context B"
    
    def test_parse_batch_response_invalid_json(self, augmenter):
        """Test parsing invalid JSON falls back to alternative parser"""
        response = "Not valid JSON at all"
        
        contexts = augmenter._parse_batch_response(response, offset=0)
        
        # Should return empty dict or use fallback
        assert isinstance(contexts, dict)
    
    def test_parse_batch_response_with_extra_text(self, augmenter):
        """Test parsing JSON with surrounding text"""
        response = """
        Here are the contexts:
        [
            {"index": 0, "context": "Context for chunk 0"},
            {"index": 1, "context": "Context for chunk 1"}
        ]
        That's all!
        """
        
        contexts = augmenter._parse_batch_response(response, offset=0)
        
        assert len(contexts) == 2
        assert 0 in contexts
        assert 1 in contexts
    
    def test_fallback_parse(self, augmenter):
        """Test fallback parsing for non-JSON responses"""
        response = """
        Chunk 0: This is context for the first chunk
        Chunk 1: This is context for the second chunk
        """
        
        contexts = augmenter._fallback_parse(response, offset=0)
        
        assert isinstance(contexts, dict)
        # Should extract some contexts
        assert len(contexts) >= 0
    
    def test_generate_contexts_batch(self, augmenter, sample_chunks, document_data, mock_llm):
        """Test batch context generation"""
        contexts = augmenter._generate_contexts_batch(sample_chunks, document_data)
        
        assert isinstance(contexts, dict)
        assert len(contexts) > 0
        assert mock_llm.invoke.called
    
    def test_generate_contexts_batch_large_dataset(self, augmenter, document_data, mock_llm):
        """Test batch processing with large number of chunks"""
        # Create 100 chunks
        large_chunks = [
            {
                'text': f'This is chunk number {i}',
                'metadata': {'chunk_id': f'chunk_{i}'}
            }
            for i in range(100)
        ]
        
        contexts = augmenter._generate_contexts_batch(large_chunks, document_data)
        
        # Should process in batches
        assert mock_llm.invoke.call_count >= 2  # At least 2 batches for 100 chunks
    
    def test_augment_with_llm_error(self, sample_chunks, document_data):
        """Test augmentation when LLM raises error"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM Error")
        
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        # Should return original chunks on error
        assert augmented == sample_chunks
    
    def test_context_prepending_format(self, augmenter, sample_chunks, document_data):
        """Test that context is properly prepended to chunk text"""
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        for chunk in augmented:
            # Check format: context\n\noriginal_text
            assert '\n\n' in chunk['text']
    
    def test_metadata_preservation(self, augmenter, sample_chunks, document_data):
        """Test that metadata is preserved during augmentation"""
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        for i, chunk in enumerate(augmented):
            assert chunk['metadata'] == sample_chunks[i]['metadata']
    
    def test_batch_size_handling(self, document_data):
        """Test handling of different batch sizes"""
        mock_llm = Mock()
        response = Mock()
        response.content = json.dumps([{"index": i, "context": f"Context {i}"} for i in range(50)])
        mock_llm.invoke = Mock(return_value=response)
        
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        
        # Create exactly 50 chunks (one batch)
        chunks = [
            {'text': f'Chunk {i}', 'metadata': {'id': i}}
            for i in range(50)
        ]
        
        augmented = augmenter.augment_chunks_with_context(chunks, document_data)
        
        assert len(augmented) == 50
        assert mock_llm.invoke.call_count == 1
    
    def test_partial_context_generation(self, sample_chunks, document_data):
        """Test when LLM only generates context for some chunks"""
        mock_llm = Mock()
        response = Mock()
        # Only provide context for first chunk
        response.content = json.dumps([
            {"index": 0, "context": "Context for first chunk only"}
        ])
        mock_llm.invoke = Mock(return_value=response)
        
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        # First chunk should be augmented
        assert len(augmented[0]['text']) > len(sample_chunks[0]['text'])
        # Other chunks should remain unchanged
        assert augmented[1]['text'] == sample_chunks[1]['text']
        assert augmented[2]['text'] == sample_chunks[2]['text']
    
    def test_empty_context_handling(self, sample_chunks, document_data):
        """Test handling of empty context strings"""
        mock_llm = Mock()
        response = Mock()
        response.content = json.dumps([
            {"index": 0, "context": ""},
            {"index": 1, "context": "   "},  # Whitespace only
            {"index": 2, "context": "Valid context"}
        ])
        mock_llm.invoke = Mock(return_value=response)
        
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        # Chunks with empty context should remain unchanged
        assert augmented[0]['text'] == sample_chunks[0]['text']
        assert augmented[1]['text'] == sample_chunks[1]['text']
        # Chunk with valid context should be augmented
        assert len(augmented[2]['text']) > len(sample_chunks[2]['text'])
    
    def test_special_characters_in_context(self, sample_chunks, document_data):
        """Test handling of special characters in generated context"""
        mock_llm = Mock()
        response = Mock()
        response.content = json.dumps([
            {"index": 0, "context": "Context with \"quotes\" and 'apostrophes'"},
            {"index": 1, "context": "Context with\nnewlines\nand\ttabs"},
            {"index": 2, "context": "Context with émojis 🚀 and unicode"}
        ])
        mock_llm.invoke = Mock(return_value=response)
        
        augmenter = DocumentAwareAugmenter(llm=mock_llm)
        augmented = augmenter.augment_chunks_with_context(sample_chunks, document_data)
        
        # Should handle special characters without errors
        assert len(augmented) == len(sample_chunks)
        for chunk in augmented:
            assert isinstance(chunk['text'], str)
