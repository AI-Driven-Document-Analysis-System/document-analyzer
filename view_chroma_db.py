#!/usr/bin/env python3
"""
ChromaDB Viewer - Print all entries in the ChromaDB collection
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore


def print_collection_info(vectorstore, collection_name):
    """Print basic information about the collection"""
    try:
        collection = vectorstore.client.get_collection(name=collection_name)
        count = collection.count()
        print(f"📊 Collection: {collection_name}")
        print(f"📄 Total documents: {count}")
        print("=" * 60)
        return collection
    except Exception as e:
        print(f"❌ Error accessing collection: {e}")
        return None


def print_all_entries(collection):
    """Print all entries in the collection with their metadata"""
    try:
        # Get all documents from the collection
        results = collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        if not results['ids']:
            print("📭 No documents found in the collection")
            return
        
        print(f"🔍 Found {len(results['ids'])} entries:\n")
        
        for i, (doc_id, document, metadata) in enumerate(zip(
            results['ids'], 
            results['documents'], 
            results['metadatas']
        ), 1):
            
            print(f"Entry #{i}")
            print(f"ID: {doc_id}")
            print(f"Metadata: {json.dumps(metadata, indent=2)}")
            print(f"Content Preview: {document[:200]}...")
            if len(document) > 200:
                print(f"Full Content Length: {len(document)} characters")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error retrieving documents: {e}")


def main():
    """Main function to view ChromaDB contents"""
    print("🔍 ChromaDB Viewer")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Configuration - use same path as application
    # db_path = os.path.join(os.path.dirname(__file__), 'data', 'chroma_db')
    db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
    collection_name = "documents"
    
    try:
        # Initialize ChromaDB connection
        print(f"🔌 Connecting to ChromaDB at: {db_path}")
        vectorstore = LangChainChromaStore(db_path, collection_name)
        
        # Get collection info
        collection = print_collection_info(vectorstore, collection_name)
        
        if collection:
            print()
            # Print all entries
            print_all_entries(collection)
            
        print("\n✅ ChromaDB viewing complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure ChromaDB exists and the app directory structure is correct.")


if __name__ == "__main__":
    main()
