import requests
import json

URL = "http://127.0.0.1:8000/api/layout-extract"

sample_data = {
    "blocks": [
        {
            "document_id": "doc_001",
            "metadata_id": "meta_001",  # Example metadata_id
            "category_id": "cat_001",   # Example category_id
            "page_number": 1,
            "bounding_box": [10, 20, 100, 200],
            "extracted_text": "Sample text on page 1",
            "element_type": "paragraph",
            "confidence": 0.95
        },
        {
            "document_id": "doc_001",
            "metadata_id": "meta_001",  # Example metadata_id
            "category_id": "cat_001",   # Example category_id
            "page_number": 2,
            "bounding_box": [50, 60, 150, 250],
            "extracted_text": "Sample text on page 2",
            "element_type": "heading",
            "confidence": 0.98
        }
    ]
}

print("Sending data:", json.dumps(sample_data, indent=2))

response = requests.post(URL, json=sample_data, headers={"Content-Type": "application/json"})

if response.status_code == 200:
    print("Success:", response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def verify_in_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT document_id, metadata_id, category_id, raw_text, layout_blocks, layout_type, is_processed, processed_at, confidence 
            FROM documentdata 
            WHERE document_id = %s
        """, ("doc_001",))
        rows = cursor.fetchall()
        for row in rows:
            print("Verified row:", row)
    except Exception as e:
        print(f"Database verification error: {e}")
    finally:
        cursor.close()
        conn.close()

if response.status_code == 200:
    verify_in_db()