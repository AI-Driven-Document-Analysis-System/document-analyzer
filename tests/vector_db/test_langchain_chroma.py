import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the app directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from langchain.schema import Document


class TestLangChainChromaStore(unittest.TestCase):
    """Test cases for LangChainChromaStore class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for the database
        self.test_dir = tempfile.mkdtemp()
        self.persist_directory = os.path.join(self.test_dir, "test_db")
        self.collection_name = "test_collection"
        
        # Create LangChainChromaStore instance
        self.store = LangChainChromaStore(self.persist_directory, self.collection_name)

    def tearDown(self):
        """Clean up after each test method."""
        # Close the vectorstore and client properly
        if hasattr(self.store, 'cleanup'):
            self.store.cleanup()
        
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
        """Test LangChainChromaStore initialization."""
        self.assertIsNotNone(self.store.client)
        self.assertEqual(self.store.persist_directory, self.persist_directory)
        self.assertEqual(self.store.collection_name, self.collection_name)
        self.assertIsNotNone(self.store.embeddings)
        self.assertIsNotNone(self.store.vectorstore)

    def test_init_with_custom_embedding_model(self):
        """Test initialization with custom embedding model."""
        store = LangChainChromaStore(
            self.persist_directory, 
            self.collection_name, 
            embedding_model="all-MiniLM-L6-v2"
        )
        self.assertIsNotNone(store.embeddings)

    def test_add_documents(self):
        """Test adding documents to the vector store."""
        documents = [
            Document(page_content="This is document 1", metadata={"source": "test1"}),
            Document(page_content="This is document 2", metadata={"source": "test2"})
        ]
        
        # Add documents
        ids = self.store.add_documents(documents)
        
        # Verify that IDs were returned
        self.assertEqual(len(ids), 2)
        self.assertIsInstance(ids[0], str)
        self.assertIsInstance(ids[1], str)

    def test_add_documents_with_custom_ids(self):
        """Test adding documents with custom IDs."""
        documents = [
            Document(page_content="This is document 1", metadata={"source": "test1"})
        ]
        custom_ids = ["custom_id_1"]
        
        # Add documents with custom IDs
        ids = self.store.add_documents(documents, custom_ids)
        
        # Verify that custom IDs were used
        self.assertEqual(ids, custom_ids)

    def test_similarity_search(self):
        """Test similarity search functionality."""
        # First add some documents
        documents = [
            Document(page_content="This is a test document about AI", metadata={"source": "test1"}),
            Document(page_content="Another test document about machine learning", metadata={"source": "test2"})
        ]
        self.store.add_documents(documents)
        
        # Perform similarity search
        results = self.store.similarity_search("AI", k=2)
        
        # Verify results
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIsInstance(result, Document)
            self.assertIn('page_content', result.__dict__)
            self.assertIn('metadata', result.__dict__)

    def test_similarity_search_with_filter(self):
        """Test similarity search with filter."""
        # First add some documents
        documents = [
            Document(page_content="Document A", metadata={"category": "A"}),
            Document(page_content="Document B", metadata={"category": "B"})
        ]
        self.store.add_documents(documents)
        
        # Perform similarity search with filter
        results = self.store.similarity_search("Document", k=2, filter={"category": "A"})
        
        # Verify results
        self.assertIsInstance(results, list)
        for result in results:
            self.assertEqual(result.metadata.get("category"), "A")

    def test_similarity_search_with_score(self):
        """Test similarity search with scores."""
        # First add some documents
        documents = [
            Document(page_content="This is a test document", metadata={"source": "test1"}),
            Document(page_content="Another test document", metadata={"source": "test2"})
        ]
        self.store.add_documents(documents)
        
        # Perform similarity search with scores
        results = self.store.similarity_search_with_score("test", k=2)
        
        # Verify results
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], Document)
            self.assertIsInstance(result[1], (int, float))

    def test_similarity_search_with_score_and_filter(self):
        """Test similarity search with scores and filter."""
        # First add some documents
        documents = [
            Document(page_content="Document A", metadata={"category": "A"}),
            Document(page_content="Document B", metadata={"category": "B"})
        ]
        self.store.add_documents(documents)
        
        # Perform similarity search with scores and filter
        results = self.store.similarity_search_with_score("Document", k=2, filter={"category": "A"})
        
        # Verify results
        self.assertIsInstance(results, list)
        for result in results:
            self.assertEqual(result[0].metadata.get("category"), "A")

    def test_as_retriever(self):
        """Test creating a retriever from the vector store."""
        # First add some documents
        documents = [
            Document(page_content="This is a test document", metadata={"source": "test1"})
        ]
        self.store.add_documents(documents)
        
        # Create retriever
        retriever = self.store.as_retriever()
        
        # Verify retriever
        self.assertIsNotNone(retriever)
        
        # Test retriever functionality
        results = retriever.get_relevant_documents("test")
        self.assertIsInstance(results, list)

    def test_as_retriever_with_custom_params(self):
        """Test creating a retriever with custom parameters."""
        # First add some documents
        documents = [
            Document(page_content="This is a test document", metadata={"source": "test1"})
        ]
        self.store.add_documents(documents)
        
        # Create retriever with custom parameters
        retriever = self.store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 1}
        )
        
        # Verify retriever
        self.assertIsNotNone(retriever)
        
        # Test retriever functionality
        results = retriever.get_relevant_documents("test")
        self.assertIsInstance(results, list)

    def test_delete_documents(self):
        """Test deleting documents from the vector store."""
        # First add some documents
        documents = [
            Document(page_content="Document to delete", metadata={"source": "test1"}),
            Document(page_content="Document to keep", metadata={"source": "test2"})
        ]
        ids = self.store.add_documents(documents)
        
        # Delete the first document
        self.store.delete_documents([ids[0]])
        
        # Verify deletion by searching (should not find deleted document)
        results = self.store.similarity_search("Document to delete", k=2)
        for result in results:
            self.assertNotEqual(result.page_content, "Document to delete")

    def test_add_empty_documents(self):
        """Test adding empty list of documents."""
        ids = self.store.add_documents([])
        self.assertEqual(ids, [])

    def test_similarity_search_empty_store(self):
        """Test similarity search on empty vector store."""
        results = self.store.similarity_search("test", k=5)
        self.assertIsInstance(results, list)

    def test_similarity_search_with_score_empty_store(self):
        """Test similarity search with score on empty vector store."""
        results = self.store.similarity_search_with_score("test", k=5)
        self.assertIsInstance(results, list)

    def test_delete_nonexistent_documents(self):
        """Test deleting non-existent document IDs."""
        # This should not raise an exception
        self.store.delete_documents(["non_existent_id"])


if __name__ == '__main__':
    unittest.main() 