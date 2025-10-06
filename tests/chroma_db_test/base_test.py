#!/usr/bin/env python3
"""
Base Test Class for ChromaDB Tests
"""

import os
import sys
import tempfile
import shutil
import time
import gc
from abc import ABC, abstractmethod

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from langchain.schema import Document


class BaseChromaDBTest(ABC):
    """Base class for all ChromaDB tests"""
    
    def __init__(self):
        self.test_db_path = None
        self.vectorstore = None
        self.last_result_details = ""
    
    def setup(self):
        """Setup test environment"""
        # Create temporary directory for test database
        self.test_db_path = tempfile.mkdtemp(prefix="chroma_test_")
        self.vectorstore = LangChainChromaStore(
            persist_directory=self.test_db_path,
            collection_name="test_documents"
        )
        print(f"Test database created at: {self.test_db_path}")
    
    def teardown(self):
        """Clean up test environment with Windows file locking fix"""
        # Step 1: Properly close ChromaDB connections
        if self.vectorstore:
            try:
                # Force cleanup of ChromaDB client
                self.vectorstore.cleanup()
                # Clear the vectorstore reference
                self.vectorstore = None
            except Exception as e:
                print(f"Warning: ChromaDB cleanup error: {e}")
        
        # Step 2: Force garbage collection to release file handles
        gc.collect()
        
        # Step 3: Small delay to allow Windows to release file locks
        time.sleep(0.1)
        
        # Step 4: Try to remove directory with retry mechanism
        if self.test_db_path and os.path.exists(self.test_db_path):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Try to remove the directory
                    shutil.rmtree(self.test_db_path, ignore_errors=False)
                    print(f"Test database cleaned up: {self.test_db_path}")
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        print(f"Cleanup attempt {attempt + 1} failed, retrying in 0.5s...")
                        time.sleep(0.5)
                        gc.collect()  # Try garbage collection again
                    else:
                        # Final attempt failed - use ignore_errors to prevent test failure
                        print(f"Warning: Could not fully clean up test directory (Windows file locking)")
                        print(f"Directory will be cleaned up when Python process exits: {self.test_db_path}")
                        try:
                            shutil.rmtree(self.test_db_path, ignore_errors=True)
                        except:
                            pass
                except Exception as e:
                    print(f"Warning: Cleanup error: {e}")
                    break
    
    def create_test_documents(self, count=10):
        """Create test documents for testing"""
        documents = []
        for i in range(count):
            doc = Document(
                page_content=f"This is test document number {i+1}. It contains sample text for testing ChromaDB functionality. The document discusses various topics including technology, science, and research.",
                metadata={
                    "document_id": f"test_doc_{i+1}",
                    "filename": f"test_file_{i+1}.pdf",
                    "source": f"test_source_{i+1}",
                    "page_number": 1,
                    "chunk_index": 0
                }
            )
            documents.append(doc)
        return documents
    
    def add_test_documents(self, count=10):
        """Add test documents to the vector store"""
        documents = self.create_test_documents(count)
        ids = self.vectorstore.add_documents(documents)
        print(f"Added {len(ids)} test documents to vector store")
        return documents, ids
    
    @abstractmethod
    def run_test(self):
        """Run the specific test - must be implemented by subclasses"""
        pass
    
    def run(self):
        """Main test execution method"""
        test_result = False
        try:
            print(f"Setting up {self.__class__.__name__}...")
            self.setup()
            
            print(f"Running {self.__class__.__name__}...")
            test_result = self.run_test()
            
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {str(e)}")
            self.last_result_details = str(e)
            test_result = False
        
        # Always try cleanup, but don't let cleanup errors affect test results
        try:
            print(f"Cleaning up {self.__class__.__name__}...")
            self.teardown()
        except Exception as cleanup_error:
            print(f"Warning: Cleanup had issues but test results are still valid")
            # Don't change test_result - cleanup issues shouldn't fail the actual test
        
        return test_result
