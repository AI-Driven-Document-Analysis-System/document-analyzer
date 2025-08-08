import unittest
import sys
import os

# Add the backend directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from vector_db.chunking import DocumentChunker


class TestDocumentChunker(unittest.TestCase):
    """Test cases for DocumentChunker class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)

    def test_init(self):
        """Test DocumentChunker initialization."""
        self.assertEqual(self.chunker.chunk_size, 1000)
        self.assertEqual(self.chunker.chunk_overlap, 200)

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
        self.assertEqual(chunker.chunk_size, 500)
        self.assertEqual(chunker.chunk_overlap, 100)

    def test_chunk_by_sentences_simple(self):
        """Test chunking simple text by sentences."""
        text = "This is sentence one. This is sentence two. This is sentence three."
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        # Verify chunks
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)
            self.assertIn('document_id', chunk['metadata'])
            self.assertIn('chunk_index', chunk['metadata'])
            self.assertIsInstance(chunk['text'], str)
            self.assertIsInstance(chunk['metadata'], dict)

    def test_chunk_by_sentences_long_text(self):
        """Test chunking long text that exceeds chunk size."""
        # Create a long text that will need multiple chunks
        sentences = ["This is a very long sentence that contains many words. "] * 50
        text = " ".join(sentences)
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        # Verify chunks
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)  # Should create multiple chunks
        
        for i, chunk in enumerate(chunks):
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)
            self.assertEqual(chunk['metadata']['chunk_index'], i)
            # Verify chunk size doesn't exceed limit (allowing for overlap)
            self.assertLessEqual(len(chunk['text']), self.chunker.chunk_size + self.chunker.chunk_overlap)

    def test_chunk_by_sentences_with_overlap(self):
        """Test that chunks have proper overlap."""
        # Create text that will create multiple chunks
        sentences = ["This is sentence number " + str(i) + ". " for i in range(20)]
        text = " ".join(sentences)
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        # Verify overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]['text']
            next_chunk = chunks[i + 1]['text']
            
            # Check if there's overlap (next chunk should start with part of current chunk)
            if len(current_chunk) > self.chunker.chunk_overlap:
                overlap_text = current_chunk[-self.chunker.chunk_overlap:]
                self.assertIn(overlap_text, next_chunk)

    def test_chunk_by_sentences_empty_text(self):
        """Test chunking empty text."""
        text = ""
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        # Should return empty list for empty text
        self.assertEqual(chunks, [])

    def test_chunk_by_sentences_single_sentence(self):
        """Test chunking single sentence."""
        text = "This is a single sentence."
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        # Should return one chunk
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['text'], text)
        self.assertEqual(chunks[0]['metadata']['chunk_index'], 0)

    def test_chunk_by_sentences_very_long_sentence(self):
        """Test chunking a sentence that exceeds chunk size."""
        # Create a very long sentence
        long_sentence = "This is a very long sentence that contains many words and will exceed the chunk size limit. " * 20
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_sentences(long_sentence, metadata)
        
        # Should create multiple chunks even for a single sentence
        self.assertGreater(len(chunks), 1)
        
        for chunk in chunks:
            self.assertLessEqual(len(chunk['text']), self.chunker.chunk_size + self.chunker.chunk_overlap)

    def test_chunk_by_layout_simple(self):
        """Test chunking simple layout data."""
        layout_data = {
            "sections": [
                {
                    "type": "paragraph",
                    "text": "This is paragraph one.",
                    "page": 1,
                    "bbox": [10, 10, 100, 50]
                },
                {
                    "type": "header",
                    "text": "This is a header.",
                    "page": 1,
                    "bbox": [10, 60, 100, 80]
                }
            ]
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Verify chunks
        self.assertIsInstance(chunks, list)
        self.assertEqual(len(chunks), 2)  # One for each section
        
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)
            self.assertIn('section_type', chunk['metadata'])
            self.assertIn('page_number', chunk['metadata'])
            self.assertIn('bbox', chunk['metadata'])
            self.assertIn('document_id', chunk['metadata'])

    def test_chunk_by_layout_with_long_sections(self):
        """Test chunking layout data with sections that exceed chunk size."""
        # Create a long paragraph that will need sub-chunking
        long_text = "This is a very long paragraph. " * 50
        
        layout_data = {
            "sections": [
                {
                    "type": "paragraph",
                    "text": long_text,
                    "page": 1,
                    "bbox": [10, 10, 100, 50]
                }
            ]
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Should create multiple chunks for the long paragraph
        self.assertGreater(len(chunks), 1)
        
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('metadata', chunk)
            self.assertEqual(chunk['metadata']['section_type'], 'paragraph')
            self.assertEqual(chunk['metadata']['page_number'], 1)

    def test_chunk_by_layout_empty_sections(self):
        """Test chunking layout data with empty sections."""
        layout_data = {
            "sections": []
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Should return empty list
        self.assertEqual(chunks, [])

    def test_chunk_by_layout_unsupported_section_types(self):
        """Test chunking layout data with unsupported section types."""
        layout_data = {
            "sections": [
                {
                    "type": "image",  # Unsupported type
                    "text": "This should be ignored",
                    "page": 1,
                    "bbox": [10, 10, 100, 50]
                },
                {
                    "type": "paragraph",  # Supported type
                    "text": "This should be processed",
                    "page": 1,
                    "bbox": [10, 10, 100, 50]
                }
            ]
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Should only process supported section types
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['metadata']['section_type'], 'paragraph')

    def test_chunk_by_layout_missing_optional_fields(self):
        """Test chunking layout data with missing optional fields."""
        layout_data = {
            "sections": [
                {
                    "type": "paragraph",
                    "text": "This is a paragraph."
                    # Missing page and bbox
                }
            ]
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Should handle missing optional fields gracefully
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['metadata']['page_number'], 1)  # Default value
        self.assertEqual(chunks[0]['metadata']['bbox'], [])  # Default value

    def test_chunk_by_layout_mixed_content(self):
        """Test chunking layout data with mixed content types."""
        layout_data = {
            "sections": [
                {
                    "type": "header",
                    "text": "Introduction",
                    "page": 1,
                    "bbox": [10, 10, 100, 30]
                },
                {
                    "type": "paragraph",
                    "text": "This is the introduction paragraph.",
                    "page": 1,
                    "bbox": [10, 40, 100, 80]
                },
                {
                    "type": "image",
                    "text": "Image caption",
                    "page": 1,
                    "bbox": [10, 90, 100, 150]
                },
                {
                    "type": "paragraph",
                    "text": "This is another paragraph.",
                    "page": 1,
                    "bbox": [10, 160, 100, 200]
                }
            ]
        }
        metadata = {"document_id": "test123", "source": "test"}
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        # Should only process paragraph and header types
        self.assertEqual(len(chunks), 3)  # 2 paragraphs + 1 header
        
        section_types = [chunk['metadata']['section_type'] for chunk in chunks]
        self.assertIn('header', section_types)
        self.assertIn('paragraph', section_types)
        self.assertNotIn('image', section_types)

    def test_chunk_by_sentences_preserves_metadata(self):
        """Test that chunking preserves all metadata fields."""
        text = "This is sentence one. This is sentence two."
        metadata = {
            "document_id": "test123",
            "source": "test",
            "custom_field": "custom_value",
            "nested": {"key": "value"}
        }
        
        chunks = self.chunker.chunk_by_sentences(text, metadata)
        
        for chunk in chunks:
            # Verify all original metadata is preserved
            for key, value in metadata.items():
                self.assertEqual(chunk['metadata'][key], value)
            # Verify chunk_index is added
            self.assertIn('chunk_index', chunk['metadata'])

    def test_chunk_by_layout_preserves_metadata(self):
        """Test that layout chunking preserves all metadata fields."""
        layout_data = {
            "sections": [
                {
                    "type": "paragraph",
                    "text": "This is a paragraph.",
                    "page": 1,
                    "bbox": [10, 10, 100, 50]
                }
            ]
        }
        metadata = {
            "document_id": "test123",
            "source": "test",
            "custom_field": "custom_value",
            "nested": {"key": "value"}
        }
        
        chunks = self.chunker.chunk_by_layout(layout_data, metadata)
        
        for chunk in chunks:
            # Verify all original metadata is preserved
            for key, value in metadata.items():
                self.assertEqual(chunk['metadata'][key], value)
            # Verify layout-specific fields are added
            self.assertIn('section_type', chunk['metadata'])
            self.assertIn('page_number', chunk['metadata'])
            self.assertIn('bbox', chunk['metadata'])
            self.assertIn('chunk_index', chunk['metadata'])


if __name__ == '__main__':
    unittest.main() 