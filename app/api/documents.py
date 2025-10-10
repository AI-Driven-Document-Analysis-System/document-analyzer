



##Minio 

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from typing import List, Optional
from ..core.dependencies import get_current_user
from ..core.database import db_manager
from ..schemas.user_schemas import UserResponse
from ..schemas.document_schemas import DocumentResponse, DocumentUploadResponse
from ..services.document_service_aws import document_service_aws as document_service
import logging
import psycopg2
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=dict)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    override_user_id: str | None = Form(default=None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a document for the current user."""
    try:
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Resolve user ID: prefer explicit override (form or header) then JWT
        user_id = None
        header_user_id = request.headers.get('x-user-id') or request.headers.get('X-User-Id')
        if override_user_id and override_user_id.strip():
            user_id = override_user_id.strip()
        elif header_user_id and header_user_id.strip():
            user_id = header_user_id.strip()
        elif hasattr(current_user, 'id') and current_user.id is not None:
            user_id = str(current_user.id)
        else:
            raise HTTPException(status_code=400, detail="No user identifier provided")
        
        # Upload document
        result = await document_service.upload_document(file, user_id)
        
        
        return {
            "success": True,
            "message": result.get("message", "Document uploaded"),
            "document_id": result.get("document_id"),
            "status": result.get("status", "unknown"),
            "file_info": {
                "filename": file.filename,
                "size": result.get("file_size", 0),
                "mime_type": result.get("mime_type", "unknown")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Upload error: {e}")
        logger.error(f"Upload error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=dict)
async def get_documents(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all documents for the current user."""
    try:
        
        # Check if current_user is valid
        if not current_user:
            raise HTTPException(status_code=400, detail="No user information provided")
        
        # Extract user ID from UserResponse (UUID only)
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token - no user ID found")
        user_id = str(current_user.id)
        
        # Test database connection and get documents
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get documents with processing status
                query = """
                    SELECT 
                        d.id, d.original_filename, d.file_size, d.upload_timestamp, 
                        d.mime_type, d.user_id, d.file_path_minio, d.thumbnail_url,
                        dp.processing_status, dp.processing_errors,
                        dc.document_type
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    LEFT JOIN document_classifications dc ON d.id = dc.document_id
                    WHERE d.user_id = %s
                    ORDER BY d.upload_timestamp DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (user_id, limit, offset))
                documents = cursor.fetchall()
                
                
                # Get total count
                cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = %s", (str(user_id),))
                total_count = cursor.fetchone()[0]

                
                # Convert to list of dictionaries
                result = []
                for i, doc in enumerate(documents):
                    doc_dict = {
                        "id": doc[0],
                        "original_filename": doc[1],
                        "file_size": doc[2],
                        "upload_date": doc[3].isoformat() if doc[3] else None,
                        "content_type": doc[4],
                        "user_id": doc[5],
                        "file_path": doc[6],
                        "thumbnail_url": document_service.get_document_download_url(doc[7]) if doc[7] else None,
                        "processing_status": doc[8] or "unknown",
                        "processing_errors": doc[9] or "unknown",
                        "document_type": doc[9] or "Unknown"
                    }
                    result.append(doc_dict)
                
                
                return {
                    "documents": result,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total_count
                    }
                }
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_documents: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/by-user", response_model=dict)
async def get_documents_by_user(
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Public endpoint: Get documents for a given user_id without JWT (use carefully)."""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        d.id, d.original_filename, d.file_size, d.upload_timestamp, 
                        d.mime_type, d.user_id, d.file_path_minio,
                        COALESCE(dp.processing_status, 'unknown') AS processing_status, dp.processing_errors
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    WHERE d.user_id = %s
                    ORDER BY d.upload_timestamp DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (user_id, limit, offset))
                documents = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = %s", (user_id,))
                total_count = cursor.fetchone()[0]

                result = []
                for doc in documents:
                    result.append({
                        "id": doc[0],
                        "original_filename": doc[1],
                        "file_size": doc[2],
                        "upload_date": doc[3].isoformat() if doc[3] else None,
                        "content_type": doc[4],
                        "user_id": doc[5],
                        "file_path": doc[6],
                        "processing_status": doc[7],
                        "processing_errors": doc[8]
                    })

                return {
                    "documents": result,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total_count
                    }
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/types", response_model=dict)
async def get_document_types(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all available document types from classifications."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT DISTINCT dc.document_type
                    FROM document_classifications dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE d.user_id = %s
                    ORDER BY dc.document_type
                """
                cursor.execute(query, (user_id,))
                types = cursor.fetchall()
                
                document_types = ["All Types"] + [doc_type[0] for doc_type in types if doc_type[0]]
                
                return {
                    "document_types": document_types
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document types: {str(e)}")

@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific document by ID."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        d.id, d.original_filename, d.file_size, d.upload_timestamp, 
                        d.mime_type, d.user_id, d.file_path_minio,
                        dp.processing_status, dp.processing_errors
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    WHERE d.id = %s AND d.user_id = %s
                """
                cursor.execute(query, (document_id, user_id))
                doc = cursor.fetchone()
                
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                return {
                    "id": doc[0],
                    "original_filename": doc[1],
                    "file_size": doc[2],
                    "upload_date": doc[3].isoformat() if doc[3] else None,
                    "content_type": doc[4],
                    "user_id": doc[5],
                    "file_path": doc[6],
                    "processing_status": doc[7] or "unknown",
                    "processing_errors": doc[8]
                }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get extracted text content from OCR processing."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT d.original_filename, dc.extracted_text, dc.entities_extracted, 
                           dp.processing_status, d.page_count
                    FROM documents d
                    LEFT JOIN document_content dc ON d.id = dc.document_id
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    WHERE d.id = %s AND d.user_id = %s
                """
                cursor.execute(query, (document_id, user_id))
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                filename, extracted_text, entities, processing_status, page_count = result
                
                if processing_status != "completed":
                    return {
                        "document_id": document_id,
                        "filename": filename,
                        "processing_status": processing_status,
                        "extracted_text": None,
                        "message": f"Document is still being processed. Status: {processing_status}"
                    }
                
                if not extracted_text:
                    return {
                        "document_id": document_id,
                        "filename": filename,
                        "processing_status": processing_status,
                        "extracted_text": None,
                        "message": "No text content extracted from this document"
                    }
                
                return {
                    "document_id": document_id,
                    "filename": filename,
                    "processing_status": processing_status,
                    "extracted_text": extracted_text,
                    "entities": json.loads(entities) if entities else None,
                    "page_count": page_count,
                    "character_count": len(extracted_text),
                    "word_count": len(extracted_text.split()) if extracted_text else 0
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document content: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get download URL for a document."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT file_path_minio FROM documents WHERE id = %s AND user_id = %s",
                    (document_id, user_id)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                file_path = result[0]
                try:
                    download_url = document_service.get_document_download_url(file_path)
                    if download_url is None:
                        raise HTTPException(status_code=503, detail="Document storage service unavailable")
                    return {"download_url": download_url}
                except Exception as storage_error:
                    raise HTTPException(status_code=503, detail="Document storage service unavailable")
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download URL: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a document."""
    try:
        user_id = str(current_user.id) if hasattr(current_user, 'id') else current_user.email
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get file path before deletion
                cursor.execute(
                    "SELECT file_path_minio, thumbnail_url FROM documents WHERE id = %s AND user_id = %s",
                    (document_id, user_id)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                file_path = result[0]
                thumb_path = result[1]
                
                # Delete document
                document_service.delete_document(file_path, thumb_path, document_id)
                
                return {"message": "Document deleted successfully"}
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/search", response_model=dict)
async def search_documents(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
):
    """Search documents with filters and return results with classifications."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        # Parse request body
        body = await request.json()
        query = body.get("query", "")
        filters = body.get("filters", {})
        document_type = filters.get("document_type", "All Types")
        date_range = filters.get("date_range", "all")
        limit = filters.get("limit", 50)
        offset = filters.get("offset", 0)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Build the base query
                base_query = """
                    SELECT DISTINCT
                        d.id, d.original_filename, d.file_size, d.upload_timestamp, 
                        d.mime_type, d.user_id, d.file_path_minio, d.page_count,
                        dp.processing_status, dp.processing_errors,
                        dc.document_type, dc.confidence_score,
                        dc_content.extracted_text
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    LEFT JOIN document_classifications dc ON d.id = dc.document_id
                    LEFT JOIN document_content dc_content ON d.id = dc_content.document_id
                    WHERE d.user_id = %s
                """
                
                params = [user_id]
                param_count = 1
                
                # Add search query filter
                if query:
                    base_query += f" AND (d.original_filename ILIKE %s OR dc_content.extracted_text ILIKE %s)"
                    params.extend([f"%{query}%", f"%{query}%"])
                    param_count += 2
                
                # Add document type filter
                if document_type and document_type != "All Types":
                    base_query += f" AND dc.document_type = %s"
                    params.append(document_type)
                    param_count += 1
                
                # Add date range filter
                if date_range != "all":
                    if date_range == "today":
                        base_query += f" AND DATE(d.upload_timestamp) = CURRENT_DATE"
                    elif date_range == "week":
                        base_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '7 days'"
                    elif date_range == "month":
                        base_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '30 days'"
                    elif date_range == "year":
                        base_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '1 year'"
                
                # Add ordering and pagination
                base_query += " ORDER BY d.upload_timestamp DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(base_query, params)
                documents = cursor.fetchall()
                
                # Get total count for pagination
                count_query = """
                    SELECT COUNT(DISTINCT d.id)
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    LEFT JOIN document_classifications dc ON d.id = dc.document_id
                    LEFT JOIN document_content dc_content ON d.id = dc_content.document_id
                    WHERE d.user_id = %s
                """
                
                count_params = [user_id]
                count_param_count = 1
                
                if query:
                    count_query += f" AND (d.original_filename ILIKE %s OR dc_content.extracted_text ILIKE %s)"
                    count_params.extend([f"%{query}%", f"%{query}%"])
                    count_param_count += 2
                
                if document_type and document_type != "All Types":
                    count_query += f" AND dc.document_type = %s"
                    count_params.append(document_type)
                    count_param_count += 1
                
                if date_range != "all":
                    if date_range == "today":
                        count_query += f" AND DATE(d.upload_timestamp) = CURRENT_DATE"
                    elif date_range == "week":
                        count_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '7 days'"
                    elif date_range == "month":
                        count_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '30 days'"
                    elif date_range == "year":
                        count_query += f" AND d.upload_timestamp >= CURRENT_DATE - INTERVAL '1 year'"
                
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]
                
                # Format results
                result = []
                for doc in documents:
                    # Extract excerpt from content (first 200 characters)
                    excerpt = ""
                    if doc[12]:  # extracted_text
                        excerpt = doc[12][:200] + "..." if len(doc[12]) > 200 else doc[12]
                    
                    doc_dict = {
                        "id": doc[0],
                        "title": doc[1],
                        "type": doc[10] or "Unknown",  # document_type
                        "excerpt": excerpt,
                        "uploadDate": doc[3].isoformat() if doc[3] else None,
                        "confidence": float(doc[11]) * 100 if doc[11] else 0,  # confidence_score
                        "pages": doc[7] or 0,  # page_count
                        "file_size": doc[2],
                        "content_type": doc[4],
                        "processing_status": doc[8] or "unknown",
                        "file_path": doc[6]
                    }
                    result.append(doc_dict)
                
                return {
                    "documents": result,
                    "total_results": total_count,
                    "query": query,
                    "filters": filters,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total_count
                    }
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.get("/{document_id}/embedding-status")
async def get_document_embedding_status(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get the embedding status of a document"""
    try:
        # Check if document exists and belongs to user
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, original_filename 
                    FROM documents 
                    WHERE id = %s AND user_id = %s
                """, (document_id, current_user.id))
                
                document = cursor.fetchone()
                if not document:
                    raise HTTPException(status_code=404, detail="Document not found")
        
        # Check embedding status
        is_embedded = document_embedding_service.check_document_embedded(document_id)
        
        # Get collection info
        collection_info = document_embedding_service.get_collection_info()
        
        return {
            "document_id": document_id,
            "filename": document[1],
            "is_embedded": is_embedded,
            "collection_info": collection_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking embedding status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking embedding status: {str(e)}")


@router.post("/{document_id}/embed")
async def manually_embed_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Manually trigger document embedding (useful if automatic embedding failed)"""
    try:
        # Check if document exists and belongs to user
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, original_filename 
                    FROM documents 
                    WHERE id = %s AND user_id = %s
                """, (document_id, current_user.id))
                
                document = cursor.fetchone()
                if not document:
                    raise HTTPException(status_code=404, detail="Document not found")
        
        # Trigger embedding
        result = document_embedding_service.embed_document(document_id)
        
        return {
            "document_id": document_id,
            "filename": document[1],
            "embedding_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error manually embedding document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error manually embedding document: {str(e)}")

@router.put("/{document_id}/save_changes")
async def update_document_content(
    document_id: str,
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update extracted text content for a document."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        user_id = str(current_user.id)
        
        # Parse request body
        body = await request.json()
        extracted_text = body.get("extracted_text")
        
        if extracted_text is None:
            raise HTTPException(status_code=400, detail="extracted_text is required")
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # First verify the document belongs to the user
                cursor.execute(
                    "SELECT id FROM documents WHERE id = %s AND user_id = %s",
                    (document_id, user_id)
                )
                doc = cursor.fetchone()
                
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                # Update the extracted text in document_content table
                cursor.execute("""
                    UPDATE document_content 
                    SET extracted_text = %s
                    WHERE document_id = %s
                """, (extracted_text, document_id))
                
                # If no rows were updated, the document_content entry doesn't exist
                if cursor.rowcount == 0:
                    # Insert new entry
                    cursor.execute("""
                        INSERT INTO document_content (document_id, extracted_text, last_modified)
                        VALUES (%s, %s, NOW())
                    """, (document_id, extracted_text))
                
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Document content updated successfully",
                    "document_id": document_id,
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating document content: {str(e)}")

#overall what this code do is define a router for the document service, which includes the following endpoints:
#GET /documents: Get a list of documents for the current user.
#POST /documents: Upload a new document for the current user.
#GET /documents/{document_id}: Get a specific document by ID.
#GET /documents/{document_id}/download: Get download URL for a document.
#DELETE /documents/{document_id}: Delete a document.
#GET /documents/{document_id}/embedding-status: Check if document is embedded in ChromaDB.
#POST /documents/{document_id}/embed: Manually trigger document embedding.
#The code uses the FastAPI framework to define the endpoints and the Pydantic models to define the request and response schemas.
#The code also uses the SQLAlchemy ORM to interact with the database and the MinIO client to interact with the object storage.
