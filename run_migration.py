#!/usr/bin/env python3
"""
Database migration script to add Google OAuth support
Run this script to add the necessary columns for Google authentication
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the Google OAuth migration"""
    try:
        # Database connection parameters
        db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'docanalyzer'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        # Try DATABASE_URL first if available
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(**db_params)
        
        cursor = conn.cursor()
        
        # Read and execute migration SQL
        with open('migrations/add_google_oauth_columns.sql', 'r') as f:
            migration_sql = f.read()
        
        print("Running Google OAuth migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("Migration completed successfully!")
        print("Added columns: google_id, is_oauth_user")
        print("Modified: password_hash (now optional)")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
