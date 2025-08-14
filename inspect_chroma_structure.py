#!/usr/bin/env python3
"""
Inspect ChromaDB Database Structure

This script shows you the actual database structure - how many rows were created
and how your documents are stored in ChromaDB.
"""

import sqlite3
import json

def inspect_chroma_structure():
    """Inspect the actual ChromaDB database structure"""
    conn = sqlite3.connect('./chroma_db/chroma.sqlite3')
    cursor = conn.cursor()
    
    print("🔍 CHROMADB DATABASE STRUCTURE")
    print("=" * 60)
    
    # Show tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📋 Tables found: {[table[0] for table in tables]}")
    
    print("\n" + "=" * 60)
    
    # Check embeddings table
    try:
        cursor.execute("SELECT COUNT(*) FROM embeddings;")
        embed_count = cursor.fetchone()[0]
        print(f"📊 Embeddings table: {embed_count} rows")
        
        if embed_count > 0:
            # Check the actual columns in embeddings table
            cursor.execute("PRAGMA table_info(embeddings);")
            columns = cursor.fetchall()
            print(f"📋 Embeddings table columns: {[col[1] for col in columns]}")
            
            # Get sample data with available columns
            cursor.execute("SELECT * FROM embeddings LIMIT 3;")
            rows = cursor.fetchall()
            
            print(f"\n📄 Sample embeddings (showing first 3):")
            for i, row in enumerate(rows, 1):
                print(f"\n--- Row {i} ---")
                for j, col in enumerate(columns):
                    if col[1] == 'embedding':
                        print(f"{col[1]}: [Vector with {len(row[j])} dimensions]")
                    else:
                        print(f"{col[1]}: {row[j]}")
    except Exception as e:
        print(f"❌ Error with embeddings table: {e}")
        embed_count = 0
    
    print("\n" + "=" * 60)
    
    # Check embedding_metadata table
    try:
        cursor.execute("SELECT COUNT(*) FROM embedding_metadata;")
        metadata_count = cursor.fetchone()[0]
        print(f"📋 Embedding metadata table: {metadata_count} rows")
        
        if metadata_count > 0:
            cursor.execute("SELECT * FROM embedding_metadata LIMIT 3;")
            rows = cursor.fetchall()
            
            print(f"\n📋 Sample metadata:")
            for i, row in enumerate(rows, 1):
                print(f"\n--- Metadata {i} ---")
                print(f"Row data: {row}")
    except Exception as e:
        print(f"❌ Error with embedding_metadata table: {e}")
        metadata_count = 0
    
    print("\n" + "=" * 60)
    
    # Summary
    print("📊 SUMMARY:")
    print(f"Total embeddings: {embed_count}")
    print(f"Total metadata entries: {metadata_count}")
    print(f"Tables found: {len(tables)}")
    
    conn.close()

if __name__ == "__main__":
    inspect_chroma_structure()
