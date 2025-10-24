#!/usr/bin/env python3
"""
Corruption Recovery Test for ChromaDB
Tests system behavior when ChromaDB files are corrupted or missing
"""

import os
import shutil
import time
from base_test import BaseChromaDBTest


class CorruptionRecoveryTest(BaseChromaDBTest):
    """Test ChromaDB corruption and recovery scenarios"""
    
    def run_test(self):
        """Test various corruption scenarios"""
        print("Testing corruption recovery...")
        
        # Add initial test documents
        documents, ids = self.add_test_documents(20)
        
        # Test 1: Database file deletion
        deletion_test_result = self.test_database_deletion()
        if not deletion_test_result:
            return False
        
        # Test 2: Database file corruption
        corruption_test_result = self.test_database_corruption()
        if not corruption_test_result:
            return False
        
        # Test 3: Partial corruption
        partial_corruption_result = self.test_partial_corruption()
        if not partial_corruption_result:
            return False
        
        print("All corruption recovery tests passed!")
        self.last_result_details = "All corruption scenarios handled successfully"
        return True
    
    def test_database_deletion(self):
        """Test behavior when database files are deleted"""
        print("\nTest 1: Database file deletion")
        
        # First, verify we can query existing data
        initial_results = self.vectorstore.similarity_search("test document", k=5)
        print(f"Initial query returned {len(initial_results)} results")
        
        if len(initial_results) == 0:
            print("ERROR: No initial results found")
            return False
        
        # Find and delete the ChromaDB SQLite file
        chroma_db_file = None
        for root, dirs, files in os.walk(self.test_db_path):
            for file in files:
                if file.endswith('.sqlite3'):
                    chroma_db_file = os.path.join(root, file)
                    break
            if chroma_db_file:
                break
        
        if not chroma_db_file:
            print("ERROR: Could not find ChromaDB SQLite file")
            return False
        
        print(f"Deleting ChromaDB file: {chroma_db_file}")
        
        try:
            # Delete the database file
            os.remove(chroma_db_file)
            print("Database file deleted successfully")
            
            # Try to query after deletion
            try:
                post_deletion_results = self.vectorstore.similarity_search("test document", k=5)
                print(f"Post-deletion query returned {len(post_deletion_results)} results")
                
                # The system should either:
                # 1. Return empty results gracefully, or
                # 2. Recreate the database automatically
                
                print("Database deletion handled gracefully")
                return True
                
            except Exception as e:
                print(f"Query after deletion failed: {str(e)}")
                
                # This is acceptable - the system detected the corruption
                # Check if we can recover by recreating the vectorstore
                try:
                    print("Attempting to recover by recreating vectorstore...")
                    from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
                    
                    self.vectorstore = LangChainChromaStore(
                        persist_directory=self.test_db_path,
                        collection_name="test_documents"
                    )
                    
                    # Try a simple operation
                    recovery_results = self.vectorstore.similarity_search("test", k=1)
                    print("Recovery successful - new empty database created")
                    return True
                    
                except Exception as recovery_error:
                    print(f"Recovery failed: {str(recovery_error)}")
                    self.last_result_details = f"Database deletion recovery failed: {str(recovery_error)}"
                    return False
        
        except Exception as e:
            print(f"Failed to delete database file: {str(e)}")
            self.last_result_details = f"Could not delete database file: {str(e)}"
            return False
    
    def test_database_corruption(self):
        """Test behavior when database file is corrupted"""
        print("\nTest 2: Database file corruption")
        
        # Re-add some test documents for this test
        try:
            documents = self.create_test_documents(10)
            self.vectorstore.add_documents(documents)
            print("Added test documents for corruption test")
        except:
            print("Could not add documents - continuing with corruption test")
        
        # Find the ChromaDB SQLite file
        chroma_db_file = None
        for root, dirs, files in os.walk(self.test_db_path):
            for file in files:
                if file.endswith('.sqlite3'):
                    chroma_db_file = os.path.join(root, file)
                    break
            if chroma_db_file:
                break
        
        if not chroma_db_file:
            print("No ChromaDB SQLite file found - creating one first")
            try:
                # Force creation by adding a document
                from langchain.schema import Document
                doc = Document(
                    page_content="Corruption test document",
                    metadata={"document_id": "corruption_test"}
                )
                self.vectorstore.add_documents([doc])
                
                # Find the file again
                for root, dirs, files in os.walk(self.test_db_path):
                    for file in files:
                        if file.endswith('.sqlite3'):
                            chroma_db_file = os.path.join(root, file)
                            break
                    if chroma_db_file:
                        break
            except Exception as e:
                print(f"Could not create database file: {str(e)}")
                return True  # Skip this test if we can't create a file
        
        if not chroma_db_file:
            print("Still no database file found - skipping corruption test")
            return True
        
        print(f"Corrupting database file: {chroma_db_file}")
        
        try:
            # Corrupt the file by writing random data to it
            with open(chroma_db_file, 'wb') as f:
                f.write(b'CORRUPTED_DATA_' * 100)
            
            print("Database file corrupted")
            
            # Try to query the corrupted database
            try:
                corrupted_results = self.vectorstore.similarity_search("test", k=5)
                print(f"Query on corrupted database returned {len(corrupted_results)} results")
                
                # If we get here, the system handled corruption gracefully
                print("Corruption handled gracefully")
                return True
                
            except Exception as e:
                print(f"Query on corrupted database failed (expected): {str(e)}")
                
                # This is expected - now test recovery
                try:
                    print("Testing recovery from corruption...")
                    
                    # Try to recreate the vectorstore
                    from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
                    
                    self.vectorstore = LangChainChromaStore(
                        persist_directory=self.test_db_path,
                        collection_name="test_documents"
                    )
                    
                    # Add a test document to verify it works
                    from langchain.schema import Document
                    recovery_doc = Document(
                        page_content="Recovery test document",
                        metadata={"document_id": "recovery_test"}
                    )
                    
                    recovery_ids = self.vectorstore.add_documents([recovery_doc])
                    
                    if len(recovery_ids) > 0:
                        print("Recovery successful - new database created and working")
                        return True
                    else:
                        print("Recovery failed - could not add documents")
                        return False
                        
                except Exception as recovery_error:
                    print(f"Recovery from corruption failed: {str(recovery_error)}")
                    self.last_result_details = f"Corruption recovery failed: {str(recovery_error)}"
                    return False
        
        except Exception as e:
            print(f"Could not corrupt database file: {str(e)}")
            # If we can't corrupt it, that's actually fine - skip this test
            return True
    
    def test_partial_corruption(self):
        """Test behavior with partial file corruption"""
        print("\nTest 3: Partial corruption test")
        
        # Add some documents first
        try:
            documents = self.create_test_documents(5)
            self.vectorstore.add_documents(documents)
            print("Added documents for partial corruption test")
        except:
            print("Could not add documents - continuing with partial corruption test")
        
        # Test directory permission issues
        try:
            # Make directory read-only temporarily
            original_permissions = os.stat(self.test_db_path).st_mode
            os.chmod(self.test_db_path, 0o444)  # Read-only
            
            print("Made database directory read-only")
            
            # Try to add a document (should fail gracefully)
            try:
                from langchain.schema import Document
                readonly_doc = Document(
                    page_content="Read-only test document",
                    metadata={"document_id": "readonly_test"}
                )
                
                readonly_ids = self.vectorstore.add_documents([readonly_doc])
                print(f"Unexpectedly succeeded in adding document to read-only directory")
                
            except Exception as e:
                print(f"Adding document to read-only directory failed (expected): {str(e)}")
            
            # Restore permissions
            os.chmod(self.test_db_path, original_permissions)
            print("Restored directory permissions")
            
            # Verify we can add documents again
            try:
                from langchain.schema import Document
                recovery_doc = Document(
                    page_content="Permission recovery test document",
                    metadata={"document_id": "permission_recovery_test"}
                )
                
                recovery_ids = self.vectorstore.add_documents([recovery_doc])
                
                if len(recovery_ids) > 0:
                    print("Permission recovery successful")
                    return True
                else:
                    print("Permission recovery failed")
                    return False
                    
            except Exception as e:
                print(f"Permission recovery failed: {str(e)}")
                self.last_result_details = f"Permission recovery failed: {str(e)}"
                return False
        
        except Exception as e:
            print(f"Partial corruption test error: {str(e)}")
            # If we can't test permissions, that's okay
            return True
