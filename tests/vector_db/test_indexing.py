import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the backend directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from vector_db.indexing import LangChainDocumentIndexer
from vector_db.langchain_chroma import LangChainChromaStore
from vector_db.chunking import DocumentChunker
from langchain.schema import Document


class TestLangChainDocumentIndexer(unittest.TestCase):
    """Test cases for LangChainDocumentIndexer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for the database
        self.test_dir = tempfile.mkdtemp()
        self.persist_directory = os.path.join(self.test_dir, "test_db")
        self.collection_name = "test_collection"
        
        # Create dependencies
        self.vectorstore = LangChainChromaStore(self.persist_directory, self.collection_name)
        self.chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
        
        # Create indexer
        self.indexer = LangChainDocumentIndexer(self.vectorstore, self.chunker)

    def tearDown(self):
        """Clean up after each test method."""
        # Close the vectorstore and client properly
        if hasattr(self.vectorstore, 'cleanup'):
            self.vectorstore.cleanup()
        
        # Remove the temporary directory
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except:
                # If files are locked, try to remove them later
                import time
                time.sleep(1)
                try:
                    shutil.rmtree(self.test_dir)
                except:
                    pass

    def test_init(self):
        """Test LangChainDocumentIndexer initialization."""
        self.assertIsNotNone(self.indexer.vectorstore)
        self.assertIsNotNone(self.indexer.chunker)
        self.assertIsNotNone(self.indexer.logger)

    def test_index_document_with_layout_data(self):
        """Test indexing a document with layout data."""
        document_data = {
            "id": "test123",
            "type": "pdf",
            "filename": "test.pdf",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "layout_data": {
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
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that IDs were returned
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)
        self.assertIsInstance(ids[0], str)

    def test_index_document_with_text_only(self):
        """Test indexing a document with text only (no layout data)."""
        document_data = {
            "id": "test123",
            "type": "txt",
            "filename": "test.txt",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "text": "This is sentence one. This is sentence two. This is sentence three."
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that IDs were returned
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)
        self.assertIsInstance(ids[0], str)

    def test_index_document_with_minimal_data(self):
        """Test indexing a document with minimal required data."""
        document_data = {
            "id": "test123",
            "text": "This is a simple document."
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that IDs were returned
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)

    def test_index_document_with_long_text(self):
        """Test indexing a document with long text that will create multiple chunks."""
        # Create long text
        long_text = "This is a very long sentence. " * 100
        
        document_data = {
            "id": "test123",
            "text": long_text
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that multiple chunks were created
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 1)

    def test_index_document_with_complex_layout(self):
        """Test indexing a document with complex layout data."""
        document_data = {
            "id": "test123",
            "type": "pdf",
            "filename": "complex.pdf",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "layout_data": {
                "sections": [
                    {
                        "type": "header",
                        "text": "Introduction",
                        "page": 1,
                        "bbox": [10, 10, 100, 30]
                    },
                    {
                        "type": "paragraph",
                        "text": "This is the introduction paragraph with some content.",
                        "page": 1,
                        "bbox": [10, 40, 100, 80]
                    },
                    {
                        "type": "image",
                        "text": "Figure 1: Example image",
                        "page": 1,
                        "bbox": [10, 90, 100, 150]
                    },
                    {
                        "type": "paragraph",
                        "text": "This is another paragraph with more content.",
                        "page": 1,
                        "bbox": [10, 160, 100, 200]
                    }
                ]
            }
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that IDs were returned (should process header and paragraphs, skip image)
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)

    def test_index_document_preserves_metadata(self):
        """Test that indexing preserves all document metadata."""
        document_data = {
            "id": "test123",
            "type": "pdf",
            "filename": "test.pdf",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "text": "This is a test document."
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that the document was indexed by searching for it
        results = self.indexer.vectorstore.similarity_search("test document", k=5)
        
        # Check that at least one result was found
        self.assertGreater(len(results), 0)
        
        # Verify that metadata was preserved in the results
        for result in results:
            self.assertIn('document_id', result.metadata)
            self.assertIn('document_type', result.metadata)
            self.assertIn('filename', result.metadata)
            self.assertIn('upload_date', result.metadata)
            self.assertIn('user_id', result.metadata)
            self.assertEqual(result.metadata['document_id'], 'test123')

    def test_index_document_with_empty_layout_data(self):
        """Test indexing a document with empty layout data."""
        document_data = {
            "id": "test123",
            "layout_data": {
                "sections": []
            }
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Should return empty list since no sections to process
        self.assertEqual(ids, [])

    def test_index_document_with_empty_text(self):
        """Test indexing a document with empty text."""
        document_data = {
            "id": "test123",
            "text": ""
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Should return empty list since no text to process
        self.assertEqual(ids, [])

    def test_index_document_error_handling(self):
        """Test that indexing properly handles errors."""
        # Mock the chunker to raise an exception
        with patch.object(self.chunker, 'chunk_by_sentences', side_effect=Exception("Chunking failed")):
            document_data = {
                "id": "test123",
                "text": "This should fail."
            }
            
            # Should raise an exception
            with self.assertRaises(Exception):
                self.indexer.index_document(document_data)

    def test_index_document_with_missing_optional_fields(self):
        """Test indexing a document with missing optional fields."""
        document_data = {
            "id": "test123",
            "text": "This is a test document."
            # Missing type, filename, upload_date, user_id
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Should work with default values for missing fields
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)

    def test_index_document_layout_vs_text_priority(self):
        """Test that layout data takes priority over text when both are present."""
        document_data = {
            "id": "test123",
            "text": "This text should be ignored.",
            "layout_data": {
                "sections": [
                    {
                        "type": "paragraph",
                        "text": "This text should be used.",
                        "page": 1,
                        "bbox": [10, 10, 100, 50]
                    }
                ]
            }
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that layout data was used
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)
        
        # Search for the content to verify layout text was used
        results = self.indexer.vectorstore.similarity_search("This text should be used", k=5)
        self.assertGreater(len(results), 0)

    def test_index_document_with_large_document(self):
        """Test indexing a very large document."""
        # Create a large document with many sections
        sections = []
        for i in range(50):
            sections.append({
                "type": "paragraph",
                "text": f"This is paragraph number {i} with some content.",
                "page": (i // 10) + 1,
                "bbox": [10, 10 + i * 20, 100, 30 + i * 20]
            })
        
        document_data = {
            "id": "large_test123",
            "type": "pdf",
            "filename": "large.pdf",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "layout_data": {
                "sections": sections
            }
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that many chunks were created
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 10)  # Should create many chunks

    def test_index_document_retrieval_verification(self):
        """Test that indexed documents can be retrieved correctly."""
        document_data = {
            "id": "retrieval_test123",
            "text": "This is a unique test document for retrieval verification."
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify retrieval
        results = self.indexer.vectorstore.similarity_search("unique test document", k=5)
        
        # Should find the indexed document
        self.assertGreater(len(results), 0)
        found = False
        for result in results:
            if "unique test document" in result.page_content:
                found = True
                break
        self.assertTrue(found, "Indexed document should be retrievable")

    def test_index_document_metadata_consistency(self):
        """Test that metadata is consistent across all chunks of a document."""
        document_data = {
            "id": "metadata_test123",
            "type": "pdf",
            "filename": "metadata_test.pdf",
            "upload_date": "2024-01-01",
            "user_id": "user123",
            "text": "This is sentence one. This is sentence two. This is sentence three. " * 20
        }
        
        # Index the document
        ids = self.indexer.index_document(document_data)
        
        # Verify that all chunks have consistent metadata
        results = self.indexer.vectorstore.similarity_search("sentence", k=10)
        
        for result in results:
            self.assertEqual(result.metadata['document_id'], 'metadata_test123')
            self.assertEqual(result.metadata['document_type'], 'pdf')
            self.assertEqual(result.metadata['filename'], 'metadata_test.pdf')
            self.assertEqual(result.metadata['upload_date'], '2024-01-01')
            self.assertEqual(result.metadata['user_id'], 'user123')


if __name__ == '__main__':
    unittest.main() 