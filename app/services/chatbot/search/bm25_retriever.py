"""
BM25 Retriever for Hybrid Search

This module provides BM25 (keyword-based) retrieval to complement semantic search.
BM25 is a statistical ranking function that scores documents based on term frequency
and inverse document frequency, making it excellent for exact keyword matches.
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
import logging
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    BM25-based document retriever for keyword matching.
    
    This retriever uses the BM25 algorithm to rank documents based on
    keyword relevance, complementing semantic search with exact term matching.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 retriever.
        
        Args:
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.tokenized_corpus = []
        self.doc_metadata = []
        self.doc_lengths = []
        self.avgdl = 0
        self.doc_freqs = {}
        self.idf = {}
        self.N = 0
        self._is_built = False
        
    def build_index(self, documents: List[Document]) -> None:
        """
        Build BM25 index from documents.
        
        Args:
            documents: List of LangChain Document objects
        """
        if not documents:
            logger.warning("No documents provided to build BM25 index")
            return
            
        logger.info(f"Building BM25 index with {len(documents)} documents...")
        
        # Extract text and metadata
        self.corpus = [doc.page_content for doc in documents]
        self.doc_metadata = [doc.metadata for doc in documents]
        
        # Tokenize corpus (simple whitespace + lowercase)
        self.tokenized_corpus = [self._tokenize(text) for text in self.corpus]
        
        # Calculate document lengths
        self.doc_lengths = [len(tokens) for tokens in self.tokenized_corpus]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Calculate document frequencies
        self.N = len(self.tokenized_corpus)
        self.doc_freqs = {}
        
        for tokens in self.tokenized_corpus:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
        
        # Calculate IDF scores
        self.idf = {}
        for term, freq in self.doc_freqs.items():
            # IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
            self.idf[term] = self._calc_idf(freq)
        
        self._is_built = True
        logger.info(f"✅ BM25 index built: {self.N} documents, {len(self.idf)} unique terms, avg_length={self.avgdl:.1f}")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization: lowercase and split by whitespace.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return text.lower().split()
    
    def _calc_idf(self, doc_freq: int) -> float:
        """
        Calculate IDF score for a term.
        
        Args:
            doc_freq: Number of documents containing the term
            
        Returns:
            IDF score
        """
        import math
        return math.log((self.N - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
    
    def _calc_bm25_score(self, query_tokens: List[str], doc_idx: int) -> float:
        """
        Calculate BM25 score for a document given query tokens.
        
        Args:
            query_tokens: Tokenized query
            doc_idx: Document index
            
        Returns:
            BM25 score
        """
        score = 0.0
        doc_tokens = self.tokenized_corpus[doc_idx]
        doc_len = self.doc_lengths[doc_idx]
        
        # Count term frequencies in document
        term_freqs = {}
        for token in doc_tokens:
            term_freqs[token] = term_freqs.get(token, 0) + 1
        
        # Calculate score for each query term
        for token in query_tokens:
            if token not in self.idf:
                continue
                
            tf = term_freqs.get(token, 0)
            idf = self.idf[token]
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, k: int = 20) -> List[Tuple[Document, float]]:
        """
        Search documents using BM25.
        
        Args:
            query: Search query
            k: Number of top results to return
            
        Returns:
            List of (Document, score) tuples
        """
        if not self._is_built:
            logger.warning("BM25 index not built, returning empty results")
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Calculate scores for all documents
        scores = []
        for idx in range(self.N):
            score = self._calc_bm25_score(query_tokens, idx)
            scores.append((idx, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k results
        top_k = scores[:k]
        
        # Convert to Document objects with scores
        results = []
        for idx, score in top_k:
            if score > 0:  # Only return documents with non-zero scores
                doc = Document(
                    page_content=self.corpus[idx],
                    metadata=self.doc_metadata[idx]
                )
                results.append((doc, score))
        
        logger.debug(f"BM25 search returned {len(results)} results for query: '{query[:50]}...'")
        return results
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing index (incremental update).
        
        Args:
            documents: List of new documents to add
        """
        if not documents:
            return
        
        logger.info(f"Adding {len(documents)} documents to BM25 index...")
        
        # Add to corpus
        for doc in documents:
            self.corpus.append(doc.page_content)
            self.doc_metadata.append(doc.metadata)
            tokens = self._tokenize(doc.page_content)
            self.tokenized_corpus.append(tokens)
            self.doc_lengths.append(len(tokens))
            
            # Update document frequencies
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
        
        # Recalculate statistics
        self.N = len(self.tokenized_corpus)
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Recalculate IDF scores
        self.idf = {}
        for term, freq in self.doc_freqs.items():
            self.idf[term] = self._calc_idf(freq)
        
        self._is_built = True
        logger.info(f"✅ BM25 index updated: {self.N} total documents")
    
    def save(self, filepath: str) -> None:
        """
        Save BM25 index to disk.
        
        Args:
            filepath: Path to save the index
        """
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'corpus': self.corpus,
                    'tokenized_corpus': self.tokenized_corpus,
                    'doc_metadata': self.doc_metadata,
                    'doc_lengths': self.doc_lengths,
                    'avgdl': self.avgdl,
                    'doc_freqs': self.doc_freqs,
                    'idf': self.idf,
                    'N': self.N,
                    'k1': self.k1,
                    'b': self.b,
                    '_is_built': self._is_built
                }, f)
            logger.info(f"✅ BM25 index saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save BM25 index: {e}")
    
    @classmethod
    def load(cls, filepath: str) -> 'BM25Retriever':
        """
        Load BM25 index from disk.
        
        Args:
            filepath: Path to load the index from
            
        Returns:
            Loaded BM25Retriever instance
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            retriever = cls(k1=data['k1'], b=data['b'])
            retriever.corpus = data['corpus']
            retriever.tokenized_corpus = data['tokenized_corpus']
            retriever.doc_metadata = data['doc_metadata']
            retriever.doc_lengths = data['doc_lengths']
            retriever.avgdl = data['avgdl']
            retriever.doc_freqs = data['doc_freqs']
            retriever.idf = data['idf']
            retriever.N = data['N']
            retriever._is_built = data['_is_built']
            
            logger.info(f"✅ BM25 index loaded from {filepath} ({retriever.N} documents)")
            return retriever
        except Exception as e:
            logger.error(f"Failed to load BM25 index: {e}")
            return cls()
    
    def is_built(self) -> bool:
        """Check if index is built."""
        return self._is_built
