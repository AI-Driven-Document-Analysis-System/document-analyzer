"""
Unit tests for BM25 Retriever
"""

import pytest
from unittest.mock import Mock, patch
from langchain.schema import Document
from app.services.chatbot.search.bm25_retriever import BM25Retriever


class TestBM25Retriever:
    """Test suite for BM25Retriever class"""
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            Document(
                page_content="The quick brown fox jumps over the lazy dog",
                metadata={"doc_id": "1", "source": "test1.txt"}
            ),
            Document(
                page_content="A fast brown fox leaps across a sleepy canine",
                metadata={"doc_id": "2", "source": "test2.txt"}
            ),
            Document(
                page_content="Python programming language is powerful and versatile",
                metadata={"doc_id": "3", "source": "test3.txt"}
            ),
            Document(
                page_content="Machine learning and artificial intelligence are transforming technology",
                metadata={"doc_id": "4", "source": "test4.txt"}
            )
        ]
    
    @pytest.fixture
    def retriever(self):
        """Create a BM25Retriever instance"""
        return BM25Retriever(k1=1.5, b=0.75)
    
    def test_initialization(self, retriever):
        """Test BM25Retriever initialization"""
        assert retriever.k1 == 1.5
        assert retriever.b == 0.75
        assert retriever.corpus == []
        assert retriever.N == 0
        assert not retriever.is_built()
    
    def test_build_index(self, retriever, sample_documents):
        """Test building BM25 index"""
        retriever.build_index(sample_documents)
        
        assert retriever.is_built()
        assert retriever.N == 4
        assert len(retriever.corpus) == 4
        assert len(retriever.tokenized_corpus) == 4
        assert len(retriever.doc_metadata) == 4
        assert retriever.avgdl > 0
        assert len(retriever.idf) > 0
    
    def test_build_index_empty_documents(self, retriever):
        """Test building index with empty document list"""
        retriever.build_index([])
        
        assert not retriever.is_built()
        assert retriever.N == 0
    
    def test_tokenization(self, retriever):
        """Test text tokenization"""
        text = "Hello World! This is a TEST."
        tokens = retriever._tokenize(text)
        
        assert tokens == ["hello", "world!", "this", "is", "a", "test."]
        assert all(isinstance(token, str) for token in tokens)
    
    def test_search_basic(self, retriever, sample_documents):
        """Test basic search functionality"""
        retriever.build_index(sample_documents)
        
        results = retriever.search("brown fox", k=2)
        
        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc, score in results)
        assert all(isinstance(score, float) for doc, score in results)
        assert all(score > 0 for doc, score in results)
    
    def test_search_exact_match(self, retriever, sample_documents):
        """Test search with exact keyword match"""
        retriever.build_index(sample_documents)
        
        results = retriever.search("python programming", k=5)
        
        assert len(results) > 0
        # The document about Python should be in results
        doc_ids = [doc.metadata["doc_id"] for doc, score in results]
        assert "3" in doc_ids
    
    def test_search_no_match(self, retriever, sample_documents):
        """Test search with no matching documents"""
        retriever.build_index(sample_documents)
        
        results = retriever.search("quantum physics", k=5)
        
        # Should return empty or very low scores
        assert len(results) == 0 or all(score < 0.1 for doc, score in results)
    
    def test_search_without_index(self, retriever):
        """Test search without building index first"""
        results = retriever.search("test query", k=5)
        
        assert results == []
    
    def test_add_documents(self, retriever, sample_documents):
        """Test adding documents to existing index"""
        # Build initial index
        retriever.build_index(sample_documents[:2])
        initial_count = retriever.N
        
        # Add more documents
        retriever.add_documents(sample_documents[2:])
        
        assert retriever.N == len(sample_documents)
        assert retriever.N > initial_count
        assert retriever.is_built()
    
    def test_add_empty_documents(self, retriever, sample_documents):
        """Test adding empty document list"""
        retriever.build_index(sample_documents)
        initial_count = retriever.N
        
        retriever.add_documents([])
        
        assert retriever.N == initial_count
    
    def test_idf_calculation(self, retriever):
        """Test IDF score calculation"""
        # Test with different document frequencies
        retriever.N = 100
        
        # Term appears in 10 documents
        idf_common = retriever._calc_idf(10)
        # Term appears in 1 document
        idf_rare = retriever._calc_idf(1)
        
        # Rare terms should have higher IDF
        assert idf_rare > idf_common
        assert idf_common > 0
        assert idf_rare > 0
    
    def test_bm25_score_calculation(self, retriever, sample_documents):
        """Test BM25 score calculation"""
        retriever.build_index(sample_documents)
        
        query_tokens = ["brown", "fox"]
        score = retriever._calc_bm25_score(query_tokens, 0)
        
        assert isinstance(score, float)
        assert score > 0
    
    def test_save_and_load(self, retriever, sample_documents, tmp_path):
        """Test saving and loading BM25 index"""
        # Build and save index
        retriever.build_index(sample_documents)
        filepath = tmp_path / "bm25_index.pkl"
        retriever.save(str(filepath))
        
        assert filepath.exists()
        
        # Load index
        loaded_retriever = BM25Retriever.load(str(filepath))
        
        assert loaded_retriever.is_built()
        assert loaded_retriever.N == retriever.N
        assert loaded_retriever.k1 == retriever.k1
        assert loaded_retriever.b == retriever.b
        assert len(loaded_retriever.corpus) == len(retriever.corpus)
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file"""
        retriever = BM25Retriever.load("nonexistent_file.pkl")
        
        assert not retriever.is_built()
        assert retriever.N == 0
    
    def test_search_ranking(self, retriever, sample_documents):
        """Test that search results are properly ranked"""
        retriever.build_index(sample_documents)
        
        results = retriever.search("brown fox", k=5)
        
        if len(results) > 1:
            # Scores should be in descending order
            scores = [score for doc, score in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_metadata_preservation(self, retriever, sample_documents):
        """Test that document metadata is preserved"""
        retriever.build_index(sample_documents)
        
        results = retriever.search("fox", k=5)
        
        for doc, score in results:
            assert "doc_id" in doc.metadata
            assert "source" in doc.metadata
    
    def test_different_k1_values(self, sample_documents):
        """Test BM25 with different k1 parameters"""
        retriever1 = BM25Retriever(k1=1.2, b=0.75)
        retriever2 = BM25Retriever(k1=2.0, b=0.75)
        
        retriever1.build_index(sample_documents)
        retriever2.build_index(sample_documents)
        
        results1 = retriever1.search("brown fox", k=3)
        results2 = retriever2.search("brown fox", k=3)
        
        # Different k1 values should produce different scores
        if results1 and results2:
            scores1 = [score for doc, score in results1]
            scores2 = [score for doc, score in results2]
            assert scores1 != scores2
    
    def test_different_b_values(self, sample_documents):
        """Test BM25 with different b parameters"""
        retriever1 = BM25Retriever(k1=1.5, b=0.5)
        retriever2 = BM25Retriever(k1=1.5, b=1.0)
        
        retriever1.build_index(sample_documents)
        retriever2.build_index(sample_documents)
        
        results1 = retriever1.search("brown fox", k=3)
        results2 = retriever2.search("brown fox", k=3)
        
        # Different b values should produce different scores
        if results1 and results2:
            scores1 = [score for doc, score in results1]
            scores2 = [score for doc, score in results2]
            assert scores1 != scores2
    
    def test_case_insensitivity(self, retriever, sample_documents):
        """Test that search is case-insensitive"""
        retriever.build_index(sample_documents)
        
        results_lower = retriever.search("python programming", k=5)
        results_upper = retriever.search("PYTHON PROGRAMMING", k=5)
        results_mixed = retriever.search("Python Programming", k=5)
        
        # All should return the same documents
        if results_lower and results_upper and results_mixed:
            docs_lower = [doc.metadata["doc_id"] for doc, _ in results_lower]
            docs_upper = [doc.metadata["doc_id"] for doc, _ in results_upper]
            docs_mixed = [doc.metadata["doc_id"] for doc, _ in results_mixed]
            
            assert docs_lower == docs_upper == docs_mixed
