#!/usr/bin/env python3
"""
Performance Test for ChromaDB
Tests insertion and query performance at different scales
"""

import time
import psutil
import os
from base_test import BaseChromaDBTest


class PerformanceTest(BaseChromaDBTest):
    """Test ChromaDB performance at different scales"""
    
    def run_test(self):
        """Test performance with different document counts"""
        print("Testing ChromaDB performance...")
        
        test_scales = [100, 500, 1000]
        results = {}
        
        for scale in test_scales:
            print(f"\nTesting with {scale} documents...")
            
            # Test insertion performance
            insertion_result = self.test_insertion_performance(scale)
            if not insertion_result:
                return False
            
            # Test query performance
            query_result = self.test_query_performance(scale)
            if not query_result:
                return False
            
            # Test memory usage
            memory_result = self.test_memory_usage(scale)
            
            results[scale] = {
                'insertion': insertion_result,
                'query': query_result,
                'memory': memory_result
            }
        
        # Print summary
        self.print_performance_summary(results)
        
        # Validate performance criteria
        return self.validate_performance_criteria(results)
    
    def test_insertion_performance(self, document_count):
        """Test document insertion performance"""
        print(f"Testing insertion of {document_count} documents...")
        
        documents = self.create_test_documents(document_count)
        
        start_time = time.time()
        ids = self.vectorstore.add_documents(documents)
        end_time = time.time()
        
        insertion_time = end_time - start_time
        docs_per_second = document_count / insertion_time
        docs_per_minute = docs_per_second * 60
        
        print(f"Insertion took {insertion_time:.2f} seconds")
        print(f"Rate: {docs_per_second:.2f} docs/second ({docs_per_minute:.2f} docs/minute)")
        
        if len(ids) == document_count:
            print("Insertion test: PASSED - All documents inserted successfully")
            return {
                'time': insertion_time,
                'rate_per_minute': docs_per_minute,
                'success': True
            }
        else:
            print(f"Insertion test: FAILED - Expected {document_count}, got {len(ids)}")
            return {
                'time': insertion_time,
                'rate_per_minute': docs_per_minute,
                'success': False
            }
    
    def test_query_performance(self, document_count):
        """Test query performance"""
        print(f"Testing query performance with {document_count} documents...")
        
        test_queries = [
            "test document technology",
            "sample text research",
            "ChromaDB functionality",
            "science and technology",
            "document number five"
        ]
        
        total_query_time = 0
        successful_queries = 0
        
        for i, query in enumerate(test_queries):
            start_time = time.time()
            results = self.vectorstore.similarity_search(query, k=5)
            end_time = time.time()
            
            query_time = end_time - start_time
            total_query_time += query_time
            
            print(f"Query {i+1}: {query_time*1000:.2f}ms ({len(results)} results)")
            
            if len(results) > 0:
                successful_queries += 1
        
        avg_query_time = total_query_time / len(test_queries)
        
        print(f"Average query time: {avg_query_time*1000:.2f}ms")
        print(f"Successful queries: {successful_queries}/{len(test_queries)}")
        
        return {
            'avg_time_ms': avg_query_time * 1000,
            'successful_queries': successful_queries,
            'total_queries': len(test_queries),
            'success': successful_queries == len(test_queries) and avg_query_time < 0.1
        }
    
    def test_memory_usage(self, document_count):
        """Test memory usage"""
        print(f"Checking memory usage with {document_count} documents...")
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        print(f"Memory usage: {memory_mb:.2f} MB")
        
        return {
            'memory_mb': memory_mb,
            'docs_per_mb': document_count / memory_mb if memory_mb > 0 else 0
        }
    
    def print_performance_summary(self, results):
        """Print performance summary"""
        print("\n" + "=" * 50)
        print("PERFORMANCE SUMMARY")
        print("=" * 50)
        
        for scale, result in results.items():
            print(f"\n{scale} Documents:")
            print(f"  Insertion: {result['insertion']['rate_per_minute']:.1f} docs/min")
            print(f"  Query: {result['query']['avg_time_ms']:.1f}ms average")
            print(f"  Memory: {result['memory']['memory_mb']:.1f}MB ({result['memory']['docs_per_mb']:.1f} docs/MB)")
    
    def validate_performance_criteria(self, results):
        """Validate performance meets criteria"""
        print("\nValidating performance criteria...")
        
        all_passed = True
        
        for scale, result in results.items():
            print(f"\n{scale} documents validation:")
            
            # Check insertion rate (should be > 100 docs/minute)
            insertion_rate = result['insertion']['rate_per_minute']
            if insertion_rate >= 100:
                print(f"  Insertion rate: PASSED ({insertion_rate:.1f} docs/min >= 100)")
            else:
                print(f"  Insertion rate: FAILED ({insertion_rate:.1f} docs/min < 100)")
                all_passed = False
            
            # Check query time (should be < 100ms)
            query_time = result['query']['avg_time_ms']
            if query_time <= 100:
                print(f"  Query time: PASSED ({query_time:.1f}ms <= 100ms)")
            else:
                print(f"  Query time: FAILED ({query_time:.1f}ms > 100ms)")
                all_passed = False
            
            # Check query success rate
            query_success = result['query']['successful_queries'] == result['query']['total_queries']
            if query_success:
                print(f"  Query success: PASSED (all queries successful)")
            else:
                print(f"  Query success: FAILED ({result['query']['successful_queries']}/{result['query']['total_queries']})")
                all_passed = False
        
        if all_passed:
            print("\nAll performance criteria met!")
            self.last_result_details = "All performance benchmarks passed"
        else:
            print("\nSome performance criteria not met!")
            self.last_result_details = "Performance benchmarks failed"
        
        return all_passed
