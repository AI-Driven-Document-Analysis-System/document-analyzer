#!/usr/bin/env python3
"""
Metadata Filtering Test for ChromaDB
Tests the accuracy and performance of document filtering by metadata
"""

import time
from base_test import BaseChromaDBTest


class MetadataFilteringTest(BaseChromaDBTest):
    """Test metadata filtering functionality"""
    
    def run_test(self):
        """Test metadata filtering accuracy and performance"""
        print("Testing metadata filtering...")
        
        # Add test documents
        documents, ids = self.add_test_documents(100)
        
        # Test 1: Filter by single document ID
        test_doc_id = "test_doc_5"
        print(f"Test 1: Filtering by document_id = {test_doc_id}")
        
        start_time = time.time()
        filtered_results = self.vectorstore.similarity_search_by_documents(
            query="test document",
            document_ids=[test_doc_id],
            k=10
        )
        filter_time = time.time() - start_time
        
        print(f"Filtered search took {filter_time*1000:.2f}ms")
        print(f"Found {len(filtered_results)} results")
        
        # Verify all results have correct document_id
        correct_filtering = True
        for doc in filtered_results:
            actual_doc_id = doc.metadata.get('document_id')
            if actual_doc_id != test_doc_id:
                print(f"ERROR: Expected {test_doc_id}, got {actual_doc_id}")
                correct_filtering = False
        
        if correct_filtering and len(filtered_results) > 0:
            print("Test 1: PASSED - Filtering by single document ID works correctly")
        else:
            print("Test 1: FAILED - Filtering by single document ID failed")
            self.last_result_details = f"Single ID filtering failed. Results: {len(filtered_results)}"
            return False
        
        # Test 2: Filter by multiple document IDs
        test_doc_ids = ["test_doc_1", "test_doc_3", "test_doc_7"]
        print(f"Test 2: Filtering by multiple document_ids = {test_doc_ids}")
        
        start_time = time.time()
        multi_filtered_results = self.vectorstore.similarity_search_by_documents(
            query="test document",
            document_ids=test_doc_ids,
            k=10
        )
        multi_filter_time = time.time() - start_time
        
        print(f"Multi-filtered search took {multi_filter_time*1000:.2f}ms")
        print(f"Found {len(multi_filtered_results)} results")
        
        # Verify all results have correct document_ids
        expected_ids = set(test_doc_ids)
        actual_ids = set(doc.metadata.get('document_id') for doc in multi_filtered_results)
        
        if actual_ids.issubset(expected_ids) and len(multi_filtered_results) > 0:
            print("Test 2: PASSED - Filtering by multiple document IDs works correctly")
        else:
            print("Test 2: FAILED - Filtering by multiple document IDs failed")
            print(f"Expected IDs: {expected_ids}")
            print(f"Actual IDs: {actual_ids}")
            self.last_result_details = f"Multi ID filtering failed. Expected: {expected_ids}, Got: {actual_ids}"
            return False
        
        # Test 3: Performance comparison (filtered vs unfiltered)
        print("Test 3: Performance comparison")
        
        start_time = time.time()
        unfiltered_results = self.vectorstore.similarity_search(
            query="test document",
            k=10
        )
        unfiltered_time = time.time() - start_time
        
        print(f"Unfiltered search took {unfiltered_time*1000:.2f}ms")
        print(f"Filtered search took {filter_time*1000:.2f}ms")
        
        performance_penalty = (filter_time - unfiltered_time) * 1000
        print(f"Performance penalty: {performance_penalty:.2f}ms")
        
        if performance_penalty < 50:  # Less than 50ms penalty is acceptable
            print("Test 3: PASSED - Performance penalty is acceptable")
        else:
            print("Test 3: FAILED - Performance penalty too high")
            self.last_result_details = f"Performance penalty too high: {performance_penalty:.2f}ms"
            return False
        
        # Test 4: Non-existent document ID
        print("Test 4: Filtering by non-existent document ID")
        
        non_existent_results = self.vectorstore.similarity_search_by_documents(
            query="test document",
            document_ids=["non_existent_doc"],
            k=10
        )
        
        if len(non_existent_results) == 0:
            print("Test 4: PASSED - Non-existent document ID returns empty results")
        else:
            print("Test 4: FAILED - Non-existent document ID returned results")
            self.last_result_details = "Non-existent document ID test failed"
            return False
        
        print("All metadata filtering tests passed!")
        self.last_result_details = f"Filter time: {filter_time*1000:.2f}ms, Performance penalty: {performance_penalty:.2f}ms"
        return True
