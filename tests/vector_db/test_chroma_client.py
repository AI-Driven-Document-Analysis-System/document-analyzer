import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from services.chatbot.vector_db.chroma_client import ChromaClient


class TestChromaClient(unittest.TestCase):
    """Test cases for ChromaClient class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for the database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_db")
        self.collection_name = "test_collection"
        
        # Mock ChromaDB client to avoid real database operations
        self.patcher = patch('chromadb.PersistentClient')
        self.mock_client_class = self.patcher.start()
        
        # Create mock client instance
        self.mock_client = Mock()
        self.mock_collection = Mock()
        
        # Set up mock collection
        self.mock_collection.name = self.collection_name
        self.mock_collection.add.return_value = {"ids": ["id1", "id2"]}
        self.mock_collection.query.return_value = {
            "documents": [["test document"]],
            "metadatas": [[{"source": "test"}]],
            "ids": [["id1"]],
            "distances": [[0.1]]
        }
        self.mock_collection.delete.return_value = None
        self.mock_collection.count.return_value = 2
        
        # Set up mock client
        self.mock_client.get_collection.return_value = self.mock_collection
        self.mock_client.create_collection.return_value = self.mock_collection
        self.mock_client_class.return_value = self.mock_client
        
        # Create ChromaClient instance
        self.client = ChromaClient(self.db_path, self.collection_name)

    def tearDown(self):
        """Clean up after each test method."""
        # Stop the patcher
        self.patcher.stop()
        
        # Remove the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test ChromaClient initialization."""
        self.assertIsNotNone(self.client.client)
        self.assertEqual(self.client.collection_name, self.collection_name)
        self.assertIsNotNone(self.client.collection)

    def test_get_or_create_collection_existing(self):
        """Test getting an existing collection."""
        # Test that collection is created successfully
        collection = self.client._get_or_create_collection()
        self.assertIsNotNone(collection)
        self.assertEqual(collection.name, self.collection_name)

    def test_get_or_create_collection_new(self):
        """Test creating a new collection when it doesn't exist."""
        # Mock the client to raise an exception when getting collection
        self.mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Create a new client instance
        client = ChromaClient(self.db_path, "new_collection")
        
        # Verify that create_collection was called
        self.mock_client.create_collection.assert_called_once()

    def test_add_documents(self):
        """Test adding documents to the collection."""
        documents = ["This is document 1", "This is document 2"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        
        # Add documents
        ids = self.client.add_documents(documents, metadatas)
        
        # Verify that IDs were returned
        self.assertEqual(len(ids), 2)
        self.assertIsInstance(ids[0], str)
        self.assertIsInstance(ids[1], str)

    def test_add_documents_with_custom_ids(self):
        """Test adding documents with custom IDs."""
        documents = ["This is document 1"]
        metadatas = [{"source": "test1"}]
        custom_ids = ["custom_id_1"]
        
        # Add documents with custom IDs
        ids = self.client.add_documents(documents, metadatas, custom_ids)
        
        # Verify that custom IDs were used
        self.assertEqual(ids, custom_ids)

    def test_query(self):
        """Test querying the collection."""
        # Query the collection
        results = self.client.query("test", n_results=2)
        
        # Verify results structure
        self.assertIn('documents', results)
        self.assertIn('metadatas', results)
        self.assertIn('ids', results)
        self.assertIn('distances', results)

    def test_query_with_where_filter(self):
        """Test querying with where filter."""
        # Query with where filter
        results = self.client.query("test", n_results=2, where={"source": "test"})
        
        # Verify results structure
        self.assertIn('documents', results)
        self.assertIn('metadatas', results)
        self.assertIn('ids', results)
        self.assertIn('distances', results)

    def test_delete_document(self):
        """Test deleting a document."""
        # Delete a document
        result = self.client.delete_document("test_id")
        
        # Verify that delete was called
        self.assertIsNone(result)

    def test_get_collection_info(self):
        """Test getting collection information."""
        # Get collection info
        info = self.client.get_collection_info()
        
        # Verify info structure
        self.assertIn('count', info)
        self.assertEqual(info['count'], 2)

    def test_add_documents_empty_list(self):
        """Test adding empty list of documents."""
        # Add empty documents list
        ids = self.client.add_documents([], [])
        
        # Should return empty list
        self.assertEqual(ids, [])

    def test_query_empty_collection(self):
        """Test querying an empty collection."""
        # Mock empty collection
        self.mock_collection.query.return_value = {
            "documents": [],
            "metadatas": [],
            "ids": [],
            "distances": []
        }
        
        # Query empty collection
        results = self.client.query("test")
        
        # Verify empty results
        self.assertEqual(len(results['documents']), 0)

    def test_invalid_document_id(self):
        """Test deleting non-existent document."""
        # Delete non-existent document
        result = self.client.delete_document("non_existent_id")
        
        # Should not raise exception
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 