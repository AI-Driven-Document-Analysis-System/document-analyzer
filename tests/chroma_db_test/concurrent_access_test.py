#!/usr/bin/env python3
"""
Concurrent Access Test for ChromaDB
Tests multiple simultaneous read/write operations
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from base_test import BaseChromaDBTest


class ConcurrentAccessTest(BaseChromaDBTest):
    """Test concurrent access to ChromaDB"""
    
    def run_test(self):
        """Test concurrent read and write operations"""
        print("Testing concurrent access...")
        
        # Add initial test documents
        documents, ids = self.add_test_documents(50)
        
        # Test 1: Concurrent reads
        read_test_result = self.test_concurrent_reads()
        if not read_test_result:
            return False
        
        # Test 2: Concurrent writes
        write_test_result = self.test_concurrent_writes()
        if not write_test_result:
            return False
        
        # Test 3: Mixed read/write operations
        mixed_test_result = self.test_mixed_operations()
        if not mixed_test_result:
            return False
        
        print("All concurrent access tests passed!")
        self.last_result_details = "All concurrent access scenarios successful"
        return True
    
    def test_concurrent_reads(self):
        """Test multiple simultaneous read operations"""
        print("\nTest 1: Concurrent reads")
        
        num_threads = 5
        queries_per_thread = 3
        
        def perform_queries(thread_id):
            """Perform queries in a thread"""
            results = []
            queries = [
                f"test document {thread_id}",
                f"sample text {thread_id}",
                f"technology research {thread_id}"
            ]
            
            for i, query in enumerate(queries):
                try:
                    start_time = time.time()
                    search_results = self.vectorstore.similarity_search(query, k=3)
                    end_time = time.time()
                    
                    results.append({
                        'thread_id': thread_id,
                        'query_id': i,
                        'query': query,
                        'results_count': len(search_results),
                        'time': end_time - start_time,
                        'success': True
                    })
                    
                except Exception as e:
                    results.append({
                        'thread_id': thread_id,
                        'query_id': i,
                        'query': query,
                        'results_count': 0,
                        'time': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            return results
        
        # Execute concurrent reads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(perform_queries, i) for i in range(num_threads)]
            all_results = []
            
            for future in as_completed(futures):
                thread_results = future.result()
                all_results.extend(thread_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_queries = sum(1 for r in all_results if r['success'])
        total_queries = len(all_results)
        avg_query_time = sum(r['time'] for r in all_results if r['success']) / successful_queries if successful_queries > 0 else 0
        
        print(f"Concurrent reads completed in {total_time:.2f}s")
        print(f"Successful queries: {successful_queries}/{total_queries}")
        print(f"Average query time: {avg_query_time*1000:.2f}ms")
        
        # Print any errors
        for result in all_results:
            if not result['success']:
                print(f"ERROR in thread {result['thread_id']}: {result.get('error', 'Unknown error')}")
        
        if successful_queries == total_queries and avg_query_time < 0.2:
            print("Concurrent reads: PASSED")
            return True
        else:
            print("Concurrent reads: FAILED")
            self.last_result_details = f"Concurrent reads failed: {successful_queries}/{total_queries} successful"
            return False
    
    def test_concurrent_writes(self):
        """Test multiple simultaneous write operations"""
        print("\nTest 2: Concurrent writes")
        
        num_threads = 3
        docs_per_thread = 10
        
        def add_documents(thread_id):
            """Add documents in a thread"""
            try:
                documents = []
                for i in range(docs_per_thread):
                    from langchain.schema import Document
                    doc = Document(
                        page_content=f"Concurrent test document from thread {thread_id}, document {i+1}. This is test content for concurrent write testing.",
                        metadata={
                            "document_id": f"concurrent_thread_{thread_id}_doc_{i+1}",
                            "filename": f"concurrent_test_{thread_id}_{i+1}.pdf",
                            "source": f"thread_{thread_id}",
                            "thread_id": thread_id
                        }
                    )
                    documents.append(doc)
                
                start_time = time.time()
                ids = self.vectorstore.add_documents(documents)
                end_time = time.time()
                
                return {
                    'thread_id': thread_id,
                    'documents_added': len(ids),
                    'expected_count': docs_per_thread,
                    'time': end_time - start_time,
                    'success': len(ids) == docs_per_thread
                }
                
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'documents_added': 0,
                    'expected_count': docs_per_thread,
                    'time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent writes
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_documents, i) for i in range(num_threads)]
            write_results = []
            
            for future in as_completed(futures):
                result = future.result()
                write_results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_writes = sum(1 for r in write_results if r['success'])
        total_docs_added = sum(r['documents_added'] for r in write_results)
        expected_total = num_threads * docs_per_thread
        
        print(f"Concurrent writes completed in {total_time:.2f}s")
        print(f"Successful write operations: {successful_writes}/{num_threads}")
        print(f"Total documents added: {total_docs_added}/{expected_total}")
        
        # Print any errors
        for result in write_results:
            if not result['success']:
                print(f"ERROR in thread {result['thread_id']}: {result.get('error', 'Unknown error')}")
        
        if successful_writes == num_threads and total_docs_added == expected_total:
            print("Concurrent writes: PASSED")
            return True
        else:
            print("Concurrent writes: FAILED")
            self.last_result_details = f"Concurrent writes failed: {total_docs_added}/{expected_total} documents added"
            return False
    
    def test_mixed_operations(self):
        """Test mixed read and write operations"""
        print("\nTest 3: Mixed read/write operations")
        
        def mixed_operations(thread_id):
            """Perform mixed read/write operations"""
            results = []
            
            try:
                # Add a document
                from langchain.schema import Document
                doc = Document(
                    page_content=f"Mixed operation test document from thread {thread_id}",
                    metadata={
                        "document_id": f"mixed_thread_{thread_id}_doc",
                        "filename": f"mixed_test_{thread_id}.pdf",
                        "source": f"mixed_thread_{thread_id}"
                    }
                )
                
                start_time = time.time()
                ids = self.vectorstore.add_documents([doc])
                add_time = time.time() - start_time
                
                results.append({
                    'operation': 'write',
                    'success': len(ids) == 1,
                    'time': add_time
                })
                
                # Perform a search
                start_time = time.time()
                search_results = self.vectorstore.similarity_search(f"mixed operation test {thread_id}", k=2)
                search_time = time.time() - start_time
                
                results.append({
                    'operation': 'read',
                    'success': len(search_results) > 0,
                    'time': search_time
                })
                
                return {
                    'thread_id': thread_id,
                    'operations': results,
                    'success': all(r['success'] for r in results)
                }
                
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'operations': results,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute mixed operations
        num_threads = 4
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(num_threads)]
            mixed_results = []
            
            for future in as_completed(futures):
                result = future.result()
                mixed_results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_threads = sum(1 for r in mixed_results if r['success'])
        
        print(f"Mixed operations completed in {total_time:.2f}s")
        print(f"Successful threads: {successful_threads}/{num_threads}")
        
        # Print any errors
        for result in mixed_results:
            if not result['success']:
                print(f"ERROR in thread {result['thread_id']}: {result.get('error', 'Unknown error')}")
        
        if successful_threads == num_threads:
            print("Mixed operations: PASSED")
            return True
        else:
            print("Mixed operations: FAILED")
            self.last_result_details = f"Mixed operations failed: {successful_threads}/{num_threads} threads successful"
            return False
