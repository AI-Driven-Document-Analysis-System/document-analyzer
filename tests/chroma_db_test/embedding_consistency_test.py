#!/usr/bin/env python3
"""
Embedding Consistency Test for ChromaDB
Tests that embeddings remain consistent across operations
"""

import time
import json
from base_test import BaseChromaDBTest


class EmbeddingConsistencyTest(BaseChromaDBTest):
    """Test embedding consistency and deterministic behavior"""
    
    def run_test(self):
        """Test embedding consistency across various scenarios"""
        print("Testing embedding consistency...")
        
        # Test 1: Deterministic embeddings
        deterministic_result = self.test_deterministic_embeddings()
        if not deterministic_result:
            return False
        
        # Test 2: Query consistency
        query_consistency_result = self.test_query_consistency()
        if not query_consistency_result:
            return False
        
        # Test 3: Restart consistency
        restart_consistency_result = self.test_restart_consistency()
        if not restart_consistency_result:
            return False
        
        print("All embedding consistency tests passed!")
        self.last_result_details = "All embedding consistency checks successful"
        return True
    
    def test_deterministic_embeddings(self):
        """Test that same content produces same embeddings"""
        print("\nTest 1: Deterministic embeddings")
        
        test_content = "This is a test document for embedding consistency testing. It contains specific text that should produce identical embeddings every time."
        
        # Create multiple documents with identical content
        from langchain.schema import Document
        documents = []
        for i in range(3):
            doc = Document(
                page_content=test_content,
                metadata={
                    "document_id": f"deterministic_test_{i+1}",
                    "filename": f"deterministic_{i+1}.pdf",
                    "source": f"deterministic_source_{i+1}"
                }
            )
            documents.append(doc)
        
        # Add documents to vector store
        ids = self.vectorstore.add_documents(documents)
        print(f"Added {len(ids)} documents with identical content")
        
        # Query for the content
        query_results = self.vectorstore.similarity_search_with_score(
            query=test_content,
            k=5
        )
        
        print(f"Query returned {len(query_results)} results")
        
        # Check that all identical documents have similar scores
        identical_scores = []
        for doc, score in query_results:
            if doc.page_content == test_content:
                identical_scores.append(score)
                print(f"Identical document score: {score:.6f}")
        
        if len(identical_scores) >= 3:
            # Check score consistency (should be very similar)
            max_score = max(identical_scores)
            min_score = min(identical_scores)
            score_difference = max_score - min_score
            
            print(f"Score range: {min_score:.6f} to {max_score:.6f} (difference: {score_difference:.6f})")
            
            if score_difference < 0.001:  # Very small tolerance for identical content
                print("Deterministic embeddings: PASSED")
                return True
            else:
                print("Deterministic embeddings: FAILED - scores too different")
                self.last_result_details = f"Score difference too large: {score_difference:.6f}"
                return False
        else:
            print("Deterministic embeddings: FAILED - not enough identical documents found")
            self.last_result_details = f"Only found {len(identical_scores)} identical documents"
            return False
    
    def test_query_consistency(self):
        """Test that same queries return consistent results"""
        print("\nTest 2: Query consistency")
        
        # Add test documents
        documents, ids = self.add_test_documents(20)
        
        test_query = "test document technology research"
        num_runs = 5
        
        print(f"Running query '{test_query}' {num_runs} times...")
        
        all_results = []
        for run in range(num_runs):
            results = self.vectorstore.similarity_search_with_score(
                query=test_query,
                k=5
            )
            all_results.append(results)
            print(f"Run {run+1}: {len(results)} results")
        
        # Check consistency across runs
        if len(all_results) == 0:
            print("Query consistency: FAILED - no results")
            return False
        
        # Compare first result with all others
        baseline_results = all_results[0]
        consistent = True
        
        for run_idx, current_results in enumerate(all_results[1:], 1):
            if len(current_results) != len(baseline_results):
                print(f"Run {run_idx+1}: Different number of results ({len(current_results)} vs {len(baseline_results)})")
                consistent = False
                continue
            
            # Check if same documents in same order
            for i, ((baseline_doc, baseline_score), (current_doc, current_score)) in enumerate(zip(baseline_results, current_results)):
                doc_id_baseline = baseline_doc.metadata.get('document_id')
                doc_id_current = current_doc.metadata.get('document_id')
                
                if doc_id_baseline != doc_id_current:
                    print(f"Run {run_idx+1}, Position {i+1}: Different document ({doc_id_current} vs {doc_id_baseline})")
                    consistent = False
                
                score_difference = abs(baseline_score - current_score)
                if score_difference > 0.0001:  # Small tolerance for floating point
                    print(f"Run {run_idx+1}, Position {i+1}: Score difference {score_difference:.6f}")
                    consistent = False
        
        if consistent:
            print("Query consistency: PASSED")
            return True
        else:
            print("Query consistency: FAILED")
            self.last_result_details = "Query results not consistent across runs"
            return False
    
    def test_restart_consistency(self):
        """Test consistency after recreating the vector store"""
        print("\nTest 3: Restart consistency")
        
        # Add test documents
        documents, ids = self.add_test_documents(10)
        
        test_query = "sample text research document"
        
        # Get baseline results
        print("Getting baseline results...")
        baseline_results = self.vectorstore.similarity_search_with_score(
            query=test_query,
            k=5
        )
        
        print(f"Baseline: {len(baseline_results)} results")
        for i, (doc, score) in enumerate(baseline_results):
            doc_id = doc.metadata.get('document_id')
            print(f"  {i+1}. {doc_id}: {score:.6f}")
        
        # Simulate restart by recreating the vector store
        print("Simulating restart by recreating vector store...")
        
        # Clean up current instance
        self.vectorstore.cleanup()
        
        # Create new instance with same path
        from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
        self.vectorstore = LangChainChromaStore(
            persist_directory=self.test_db_path,
            collection_name="test_documents"
        )
        
        # Get results after restart
        print("Getting post-restart results...")
        restart_results = self.vectorstore.similarity_search_with_score(
            query=test_query,
            k=5
        )
        
        print(f"Post-restart: {len(restart_results)} results")
        for i, (doc, score) in enumerate(restart_results):
            doc_id = doc.metadata.get('document_id')
            print(f"  {i+1}. {doc_id}: {score:.6f}")
        
        # Compare results
        if len(baseline_results) != len(restart_results):
            print(f"Restart consistency: FAILED - different result counts ({len(restart_results)} vs {len(baseline_results)})")
            self.last_result_details = f"Result count mismatch: {len(restart_results)} vs {len(baseline_results)}"
            return False
        
        consistent = True
        for i, ((baseline_doc, baseline_score), (restart_doc, restart_score)) in enumerate(zip(baseline_results, restart_results)):
            baseline_id = baseline_doc.metadata.get('document_id')
            restart_id = restart_doc.metadata.get('document_id')
            
            if baseline_id != restart_id:
                print(f"Position {i+1}: Different document ({restart_id} vs {baseline_id})")
                consistent = False
            
            score_difference = abs(baseline_score - restart_score)
            if score_difference > 0.0001:
                print(f"Position {i+1}: Score difference {score_difference:.6f}")
                consistent = False
        
        if consistent:
            print("Restart consistency: PASSED")
            return True
        else:
            print("Restart consistency: FAILED")
            self.last_result_details = "Results not consistent after restart"
            return False
