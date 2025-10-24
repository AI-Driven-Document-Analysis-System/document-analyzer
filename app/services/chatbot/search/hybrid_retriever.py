"""
Hybrid Retriever combining BM25 and Semantic Search

This module implements hybrid search using Reciprocal Rank Fusion (RRF)
to combine BM25 keyword search with semantic vector search.
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from ..vector_db.langchain_chroma import LangChainChromaStore
from .bm25_retriever import BM25Retriever
import logging

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever combining BM25 and semantic search using RRF.
    
    This retriever merges results from both BM25 (keyword-based) and
    semantic (embedding-based) search to provide better retrieval quality.
    """
    
    def __init__(
        self,
        vectorstore: LangChainChromaStore,
        bm25_retriever: BM25Retriever,
        rrf_k: int = 60
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vectorstore: ChromaDB vector store for semantic search
            bm25_retriever: BM25 retriever for keyword search
            rrf_k: RRF constant (default: 60, standard value)
        """
        self.vectorstore = vectorstore
        self.bm25_retriever = bm25_retriever
        self.rrf_k = rrf_k
    
    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[Document, float]],
        semantic_results: List[Tuple[Document, float]],
        k: int
    ) -> List[Document]:
        """
        Merge results using Reciprocal Rank Fusion (RRF).
        
        RRF formula: score = sum(1 / (k + rank_i)) for each result list
        
        Args:
            bm25_results: Results from BM25 search with scores
            semantic_results: Results from semantic search with scores
            k: Number of final results to return
            
        Returns:
            Merged and ranked list of documents
        """
        # Create document ID to content mapping
        doc_scores = {}
        doc_objects = {}
        
        # Process BM25 results
        for rank, (doc, score) in enumerate(bm25_results, start=1):
            # Use chunk_id as unique identifier, fallback to content hash
            doc_id = doc.metadata.get('chunk_id', hash(doc.page_content))
            rrf_score = 1.0 / (self.rrf_k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc
            
        # Process semantic results
        for rank, (doc, score) in enumerate(semantic_results, start=1):
            doc_id = doc.metadata.get('chunk_id', hash(doc.page_content))
            rrf_score = 1.0 / (self.rrf_k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc
        
        # Sort by RRF score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top k documents
        result = [doc_objects[doc_id] for doc_id, score in sorted_docs[:k]]
        
        logger.debug(
            f"RRF merged {len(bm25_results)} BM25 + {len(semantic_results)} semantic "
            f"results into {len(result)} final results"
        )
        
        return result
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """
        Perform hybrid search combining BM25 and semantic search.
        
        Args:
            query: Search query
            k: Number of final results to return
            filter: Optional metadata filter for semantic search
            
        Returns:
            List of top k documents
        """
        # Retrieve more results from each method for better fusion
        retrieval_k = k * 4  # Get 4x results for fusion
        
        # BM25 search
        bm25_results = []
        if self.bm25_retriever.is_built():
            bm25_results = self.bm25_retriever.search(query, k=retrieval_k)
            logger.debug(f"BM25 retrieved {len(bm25_results)} results")
        else:
            logger.warning("BM25 index not built, using semantic search only")
        
        # Semantic search
        semantic_results = self.vectorstore.similarity_search_with_score(
            query,
            k=retrieval_k,
            filter=filter
        )
        logger.debug(f"Semantic search retrieved {len(semantic_results)} results")
        
        # If BM25 is not available, return semantic results only
        if not bm25_results:
            return [doc for doc, score in semantic_results[:k]]
        
        # Merge using RRF
        merged_results = self._reciprocal_rank_fusion(
            bm25_results,
            semantic_results,
            k=k
        )
        
        return merged_results
    
    def search_by_documents(
        self,
        query: str,
        document_ids: List[str],
        k: int = 5
    ) -> List[Document]:
        """
        Perform hybrid search filtered by specific document IDs.
        
        Args:
            query: Search query
            document_ids: List of document IDs to filter by
            k: Number of final results to return
            
        Returns:
            List of top k documents from specified documents
        """
        # Retrieve more results for fusion
        retrieval_k = k * 4
        
        # BM25 search (filter results by document_id after retrieval)
        bm25_results = []
        if self.bm25_retriever.is_built():
            all_bm25_results = self.bm25_retriever.search(query, k=retrieval_k * 2)
            # Filter by document_id
            bm25_results = [
                (doc, score) for doc, score in all_bm25_results
                if doc.metadata.get('document_id') in document_ids
            ][:retrieval_k]
            logger.debug(f"BM25 retrieved {len(bm25_results)} filtered results")
        
        # Semantic search with filter
        filter_dict = {"document_id": {"$in": document_ids}}
        semantic_results = self.vectorstore.similarity_search_with_score(
            query,
            k=retrieval_k,
            filter=filter_dict
        )
        logger.debug(f"Semantic search retrieved {len(semantic_results)} filtered results")
        
        # If BM25 is not available, return semantic results only
        if not bm25_results:
            return [doc for doc, score in semantic_results[:k]]
        
        # Merge using RRF
        merged_results = self._reciprocal_rank_fusion(
            bm25_results,
            semantic_results,
            k=k
        )
        
        return merged_results
