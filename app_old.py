from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from dotenv import load_dotenv
import os
import json

app = FastAPI()

load_dotenv()

class LayoutBlock(BaseModel):
    document_id: str
    metadata_id: Optional[str] = None  # Optional since not always provided in test data
    category_id: Optional[str] = None  # Optional since not always provided in test data
    page_number: Optional[int] = None
    bounding_box: List[int]
    extracted_text: str
    element_type: Optional[str] = None
    confidence: Optional[float] = None

class LayoutBlockRequest(BaseModel):
    blocks: List[LayoutBlock]

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

@app.post("/api/layout-extract")
def save_layout_blocks(request: LayoutBlockRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for block in request.blocks:
            # Include page_number and bounding_box in the layout_blocks JSON
            layout_blocks_data = {
                "page_number": block.page_number,
                "bounding_box": block.bounding_box
            }
            cursor.execute(
                """
                INSERT INTO documentdata 
                (document_id, metadata_id, category_id, raw_text, layout_blocks, layout_type, is_processed, processed_at, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    block.document_id,
                    block.metadata_id,  # May be None if not provided
                    block.category_id,  # May be None if not provided
                    block.extracted_text,  # Using extracted_text as raw_text
                    json.dumps(layout_blocks_data),
                    block.element_type,  # Mapping element_type to layout_type
                    False,  # Default is_processed to False
                    None,   # Default processed_at to NULL
                    block.confidence
                )
            )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        cursor.close()
        conn.close()
    return {"message": "Layout blocks saved successfully", "count": len(request.blocks)}