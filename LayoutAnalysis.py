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
            cursor.execute(
                """
                INSERT INTO documentdata 
                (document_id, page_number, layout_blocks, extracted_text, layout_type, confidence)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    block.document_id,
                    block.page_number,
                    json.dumps({"bounding_box": block.bounding_box}),
                    block.extracted_text,
                    block.element_type,
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