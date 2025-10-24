#!/usr/bin/env python3
"""
Integration Test for ChromaDB
Tests integration with PostgreSQL and overall system behavior
"""

import time
import tempfile
import os
from base_test import BaseChromaDBTest


class IntegrationTest(BaseChromaDBTest):
    """Test ChromaDB integration with other system components"""
    
    def run_test(self):
        """Test integration scenarios"""
        print("Testing ChromaDB integration...")
        
        # Test 1: Memory usage scaling
        memory_scaling_result = self.test_memory_scaling()
        if not memory_scaling_result:
            return False
        
        # Test 2: Large document handling
        large_document_result = self.test_large_document_handling()
        if not large_document_result:
            return False
        
        # Test 3: Metadata validation
        metadata_validation_result = self.test_metadata_validation()
        if not metadata_validation_result:
            return False
        
        # Test 4: Collection management
        collection_management_result = self.test_collection_management()
        if not collection_management_result:
            return False
        
        print("All integration tests passed!")
        self.last_result_details = "All integration scenarios successful"
        return True
    
    def test_memory_scaling(self):
        """Test memory usage with increasing document counts"""
        print("\nTest 1: Memory usage scaling")
        
        import psutil
        process = psutil.Process(os.getpid())
        
        scales = [50, 100, 200]
        memory_usage = []
        
        for scale in scales:
            print(f"Testing with {scale} documents...")
            
            # Clear existing documents
            try:
                self.vectorstore.cleanup()
                from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
                self.vectorstore = LangChainChromaStore(
                    persist_directory=self.test_db_path,
                    collection_name="test_documents"
                )
            except:
                pass
            
            # Add documents
            documents, ids = self.add_test_documents(scale)
            
            # Measure memory
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_usage.append((scale, memory_mb))
            
            print(f"  {scale} documents: {memory_mb:.2f} MB")
        
        # Check if memory scaling is reasonable (should be roughly linear)
        if len(memory_usage) >= 2:
            first_scale, first_memory = memory_usage[0]
            last_scale, last_memory = memory_usage[-1]
            
            memory_per_doc_first = first_memory / first_scale
            memory_per_doc_last = last_memory / last_scale
            
            print(f"Memory per document: {memory_per_doc_first:.4f} MB -> {memory_per_doc_last:.4f} MB")
            
            # Memory per document shouldn't increase dramatically
            if memory_per_doc_last <= memory_per_doc_first * 2:
                print("Memory scaling: PASSED - reasonable scaling")
                return True
            else:
                print("Memory scaling: FAILED - memory usage growing too fast")
                self.last_result_details = f"Memory per doc increased from {memory_per_doc_first:.4f} to {memory_per_doc_last:.4f} MB"
                return False
        else:
            print("Memory scaling: PASSED - insufficient data for comparison")
            return True
    
    def test_large_document_handling(self):
        """Test handling of large documents"""
        print("\nTest 2: Large document handling")
        
        # Create documents of varying sizes
        from langchain.schema import Document
        
        large_documents = []
        sizes = [1000, 5000, 10000]  # Character counts
        
        for i, size in enumerate(sizes):
            content = "Large document test content. " * (size // 30)  # Approximate size
            content = content[:size]  # Exact size
            
            doc = Document(
                page_content=content,
                metadata={
                    "document_id": f"large_doc_{i+1}",
                    "filename": f"large_document_{i+1}.pdf",
                    "source": f"large_test_{i+1}",
                    "content_size": len(content)
                }
            )
            large_documents.append(doc)
        
        print(f"Created {len(large_documents)} large documents")
        for i, doc in enumerate(large_documents):
            size = len(doc.page_content)
            print(f"  Document {i+1}: {size} characters")
        
        # Add large documents
        try:
            start_time = time.time()
            ids = self.vectorstore.add_documents(large_documents)
            end_time = time.time()
            
            add_time = end_time - start_time
            print(f"Added large documents in {add_time:.2f} seconds")
            
            if len(ids) == len(large_documents):
                print("Large document addition: PASSED")
            else:
                print(f"Large document addition: FAILED - {len(ids)}/{len(large_documents)} added")
                return False
            
        except Exception as e:
            print(f"Large document addition: FAILED - {str(e)}")
            self.last_result_details = f"Large document handling failed: {str(e)}"
            return False
        
        # Test querying large documents
        try:
            query_results = self.vectorstore.similarity_search("Large document test content", k=3)
            print(f"Query returned {len(query_results)} results")
            
            # Verify we can retrieve the large documents
            found_large_docs = 0
            for doc in query_results:
                if "large_doc_" in doc.metadata.get('document_id', ''):
                    found_large_docs += 1
            
            if found_large_docs > 0:
                print("Large document querying: PASSED")
                return True
            else:
                print("Large document querying: FAILED - no large documents found")
                self.last_result_details = "Could not retrieve large documents"
                return False
                
        except Exception as e:
            print(f"Large document querying: FAILED - {str(e)}")
            self.last_result_details = f"Large document querying failed: {str(e)}"
            return False
    
    def test_metadata_validation(self):
        """Test metadata handling and validation"""
        print("\nTest 3: Metadata validation")
        
        from langchain.schema import Document
        
        # Test various metadata scenarios
        test_cases = [
            {
                "name": "Normal metadata",
                "metadata": {
                    "document_id": "meta_test_1",
                    "filename": "normal.pdf",
                    "source": "test_source",
                    "page_number": 1
                }
            },
            {
                "name": "Special characters in metadata",
                "metadata": {
                    "document_id": "meta_test_2",
                    "filename": "special-chars_file@#$.pdf",
                    "source": "test/source/with/slashes",
                    "page_number": 2
                }
            },
            {
                "name": "Unicode metadata",
                "metadata": {
                    "document_id": "meta_test_3",
                    "filename": "unicode_文档.pdf",
                    "source": "测试源",
                    "page_number": 3
                }
            },
            {
                "name": "Large metadata values",
                "metadata": {
                    "document_id": "meta_test_4",
                    "filename": "large_metadata.pdf",
                    "source": "x" * 1000,  # Large string
                    "page_number": 4,
                    "description": "y" * 500
                }
            }
        ]
        
        documents = []
        for i, test_case in enumerate(test_cases):
            doc = Document(
                page_content=f"Metadata test document {i+1} for testing {test_case['name']}",
                metadata=test_case['metadata']
            )
            documents.append(doc)
        
        # Add documents with various metadata
        try:
            ids = self.vectorstore.add_documents(documents)
            print(f"Added {len(ids)} documents with various metadata")
            
            if len(ids) != len(documents):
                print("Metadata validation: FAILED - not all documents added")
                return False
                
        except Exception as e:
            print(f"Metadata validation: FAILED - {str(e)}")
            self.last_result_details = f"Metadata validation failed: {str(e)}"
            return False
        
        # Test querying and metadata retrieval
        try:
            for test_case in test_cases:
                doc_id = test_case['metadata']['document_id']
                results = self.vectorstore.similarity_search_by_documents(
                    query="metadata test",
                    document_ids=[doc_id],
                    k=1
                )
                
                if len(results) == 1:
                    retrieved_metadata = results[0].metadata
                    original_metadata = test_case['metadata']
                    
                    # Check key metadata fields
                    if retrieved_metadata.get('document_id') == original_metadata.get('document_id'):
                        print(f"  {test_case['name']}: PASSED")
                    else:
                        print(f"  {test_case['name']}: FAILED - metadata mismatch")
                        return False
                else:
                    print(f"  {test_case['name']}: FAILED - document not found")
                    return False
            
            print("Metadata validation: PASSED")
            return True
            
        except Exception as e:
            print(f"Metadata retrieval: FAILED - {str(e)}")
            self.last_result_details = f"Metadata retrieval failed: {str(e)}"
            return False
    
    def test_collection_management(self):
        """Test collection creation and management"""
        print("\nTest 4: Collection management")
        
        try:
            # Test getting collection info
            collection = self.vectorstore.client.get_collection(name="test_documents")
            initial_count = collection.count()
            print(f"Initial collection count: {initial_count}")
            
            # Add some documents
            documents, ids = self.add_test_documents(10)
            
            # Check count after addition
            updated_count = collection.count()
            print(f"Updated collection count: {updated_count}")
            
            if updated_count >= initial_count + 10:
                print("Document counting: PASSED")
            else:
                print("Document counting: FAILED")
                return False
            
            # Test collection metadata
            try:
                # Get some documents to check structure
                results = collection.get(limit=5, include=['documents', 'metadatas'])
                
                if results and 'documents' in results and len(results['documents']) > 0:
                    print(f"Retrieved {len(results['documents'])} documents from collection")
                    print("Collection structure: PASSED")
                else:
                    print("Collection structure: FAILED - no documents retrieved")
                    return False
                    
            except Exception as e:
                print(f"Collection metadata test: FAILED - {str(e)}")
                return False
            
            # Test collection persistence
            try:
                # Cleanup and recreate to test persistence
                self.vectorstore.cleanup()
                
                from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
                new_vectorstore = LangChainChromaStore(
                    persist_directory=self.test_db_path,
                    collection_name="test_documents"
                )
                
                # Check if data persisted
                new_collection = new_vectorstore.client.get_collection(name="test_documents")
                persisted_count = new_collection.count()
                
                print(f"Persisted document count: {persisted_count}")
                
                if persisted_count > 0:
                    print("Collection persistence: PASSED")
                    self.vectorstore = new_vectorstore  # Update for cleanup
                    return True
                else:
                    print("Collection persistence: FAILED - no documents persisted")
                    self.last_result_details = "Collection persistence failed"
                    return False
                    
            except Exception as e:
                print(f"Collection persistence test: FAILED - {str(e)}")
                self.last_result_details = f"Collection persistence failed: {str(e)}"
                return False
            
        except Exception as e:
            print(f"Collection management: FAILED - {str(e)}")
            self.last_result_details = f"Collection management failed: {str(e)}"
            return False
