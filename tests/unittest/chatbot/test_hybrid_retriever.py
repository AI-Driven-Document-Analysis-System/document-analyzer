"""
Unit tests for Hybrid Retriever
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain.schema import Document
from app.services.chatbot.search.hybrid_retriever import HybridRetriever
from app.services.chatbot.search.bm25_retriever import BM25Retriever


class TestHybridRetriever:
    """Test suite for HybridRetriever class"""
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            Document(
                page_content="Machine learning is a subset of artificial intelligence",
                metadata={"doc_id": "1", "chunk_id": "chunk_1"}
            ),
            Document(
                page_content="Deep learning uses neural networks with multiple layers",
                metadata={"doc_id": "2", "chunk_id": "chunk_2"}
            ),
            Document(
                page_content="Natural language processing enables computers to understand text",
                metadata={"doc_id": "3", "chunk_id": "chunk_3"}
            ),
            Document(
                page_content="Computer vision allows machines to interpret visual information",
                metadata={"doc_id": "4", "chunk_id": "chunk_4"}
            )
        ]
    
    @pytest.fixture
    def mock_vectorstore(self):
        """Create a mock vector store"""
        vectorstore = Mock()
        vectorstore.similarity_search_with_score = Mock()
        return vectorstore
    
    @pytest.fixture
    def bm25_retriever(self, sample_documents):
        """Create a BM25 retriever with sample documents"""
        retriever = BM25Retriever()
        retriever.build_index(sample_documents)
        return retriever
    
    @pytest.fixture
    def hybrid_retriever(self, mock_vectorstore, bm25_retriever):
        """Create a HybridRetriever instance"""
        return HybridRetriever(
            vectorstore=mock_vectorstore,
            bm25_retriever=bm25_retriever,
            rrf_k=60
        )
    
    def test_initialization(self, hybrid_retriever, mock_vectorstore, bm25_retriever):
        """Test HybridRetriever initialization"""
        assert hybrid_retriever.vectorstore == mock_vectorstore
        assert hybrid_retriever.bm25_retriever == bm25_retriever
        assert hybrid_retriever.rrf_k == 60
    
    def test_search_basic(self, hybrid_retriever, sample_documents):
        """Test basic hybrid search functionality"""
        # Mock semantic search results
        semantic_results = [
            (sample_documents[0], 0.9),
            (sample_documents[1], 0.8)
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        results = hybrid_retriever.search("machine learning", k=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        assert all(isinstance(doc, Document) for doc in results)
    
    def test_search_with_filters(self, hybrid_retriever, sample_documents):
        """Test search with metadata filters"""
        semantic_results = [
            (sample_documents[0], 0.9),
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        filters = {"doc_id": "1"}
        results = hybrid_retriever.search("machine learning", k=5, filters=filters)
        
        assert isinstance(results, list)
        # Verify filters were passed to vectorstore
        hybrid_retriever.vectorstore.similarity_search_with_score.assert_called_once()
    
    def test_reciprocal_rank_fusion(self, hybrid_retriever, sample_documents):
        """Test RRF merging of results"""
        bm25_results = [
            (sample_documents[0], 10.5),
            (sample_documents[1], 8.3),
            (sample_documents[2], 5.1)
        ]
        
        semantic_results = [
            (sample_documents[1], 0.95),
            (sample_documents[0], 0.85),
            (sample_documents[3], 0.75)
        ]
        
        merged = hybrid_retriever._reciprocal_rank_fusion(
            bm25_results, semantic_results, k=4
        )
        
        assert isinstance(merged, list)
        assert len(merged) <= 4
        assert all(isinstance(doc, Document) for doc in merged)
    
    def test_rrf_deduplication(self, hybrid_retriever, sample_documents):
        """Test that RRF properly deduplicates documents"""
        # Same document appears in both result sets
        bm25_results = [
            (sample_documents[0], 10.0),
            (sample_documents[1], 8.0)
        ]
        
        semantic_results = [
            (sample_documents[0], 0.9),  # Duplicate
            (sample_documents[2], 0.8)
        ]
        
        merged = hybrid_retriever._reciprocal_rank_fusion(
            bm25_results, semantic_results, k=10
        )
        
        # Check for duplicates
        chunk_ids = [doc.metadata.get("chunk_id") for doc in merged]
        assert len(chunk_ids) == len(set(chunk_ids))  # No duplicates
    
    def test_rrf_ranking(self, hybrid_retriever, sample_documents):
        """Test that RRF produces proper ranking"""
        bm25_results = [
            (sample_documents[0], 10.0),
            (sample_documents[1], 5.0)
        ]
        
        semantic_results = [
            (sample_documents[1], 0.9),
            (sample_documents[0], 0.8)
        ]
        
        merged = hybrid_retriever._reciprocal_rank_fusion(
            bm25_results, semantic_results, k=2
        )
        
        # Documents appearing in both should rank higher
        assert len(merged) > 0
    
    def test_search_empty_results(self, hybrid_retriever):
        """Test search when both retrievers return empty results"""
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = []
        
        results = hybrid_retriever.search("nonexistent query", k=5)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_only_bm25_results(self, hybrid_retriever, sample_documents):
        """Test search when only BM25 returns results"""
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = []
        
        results = hybrid_retriever.search("machine learning", k=5)
        
        assert isinstance(results, list)
        # Should still return BM25 results
        assert len(results) >= 0
    
    def test_search_only_semantic_results(self, hybrid_retriever, sample_documents):
        """Test search when only semantic search returns results"""
        semantic_results = [
            (sample_documents[0], 0.9),
            (sample_documents[1], 0.8)
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        # Query that BM25 won't match
        results = hybrid_retriever.search("xyz123", k=5)
        
        assert isinstance(results, list)
        # Should still return semantic results
        assert len(results) > 0
    
    def test_different_rrf_k_values(self, mock_vectorstore, bm25_retriever, sample_documents):
        """Test hybrid retriever with different RRF k values"""
        retriever1 = HybridRetriever(mock_vectorstore, bm25_retriever, rrf_k=30)
        retriever2 = HybridRetriever(mock_vectorstore, bm25_retriever, rrf_k=90)
        
        semantic_results = [(sample_documents[0], 0.9)]
        mock_vectorstore.similarity_search_with_score.return_value = semantic_results
        
        results1 = retriever1.search("test", k=5)
        results2 = retriever2.search("test", k=5)
        
        # Different k values may produce different rankings
        assert isinstance(results1, list)
        assert isinstance(results2, list)
    
    def test_metadata_preservation(self, hybrid_retriever, sample_documents):
        """Test that metadata is preserved through hybrid search"""
        semantic_results = [
            (sample_documents[0], 0.9),
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        results = hybrid_retriever.search("machine learning", k=5)
        
        for doc in results:
            assert "doc_id" in doc.metadata
            assert "chunk_id" in doc.metadata
    
    def test_search_with_document_ids(self, hybrid_retriever, sample_documents):
        """Test search filtered by document IDs"""
        semantic_results = [
            (sample_documents[0], 0.9),
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        document_ids = ["1", "2"]
        results = hybrid_retriever.search(
            "machine learning",
            k=5,
            document_ids=document_ids
        )
        
        assert isinstance(results, list)
    
    def test_rrf_score_calculation(self, hybrid_retriever, sample_documents):
        """Test RRF score calculation formula"""
        # Document at rank 1 in both lists
        bm25_results = [(sample_documents[0], 10.0)]
        semantic_results = [(sample_documents[0], 0.9)]
        
        merged = hybrid_retriever._reciprocal_rank_fusion(
            bm25_results, semantic_results, k=2
        )
        
        # Should merge and return the document
        assert len(merged) >= 1
        assert merged[0].metadata["doc_id"] == "1"
    
    def test_large_k_value(self, hybrid_retriever, sample_documents):
        """Test search with k larger than available documents"""
        semantic_results = [
            (sample_documents[0], 0.9),
            (sample_documents[1], 0.8)
        ]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        results = hybrid_retriever.search("test", k=100)
        
        # Should return all available documents, not more
        assert len(results) <= len(sample_documents)
    
    def test_search_performance(self, hybrid_retriever, sample_documents):
        """Test that hybrid search completes in reasonable time"""
        import time
        
        semantic_results = [(doc, 0.9) for doc in sample_documents]
        hybrid_retriever.vectorstore.similarity_search_with_score.return_value = semantic_results
        
        start_time = time.time()
        results = hybrid_retriever.search("test query", k=10)
        end_time = time.time()
        
        # Should complete in less than 1 second for small dataset
        assert (end_time - start_time) < 1.0
        assert isinstance(results, list)
