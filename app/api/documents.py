



# from fastapi import APIRouter, HTTPException, Depends
# from ..api.auth import get_current_user
# from ..core.database import db_manager
# from ..schemas.user_schemas import UserResponse
# import logging
# import psycopg2

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/documents", tags=["documents"])

# @router.get("/")
# async def get_documents(current_user: UserResponse = Depends(get_current_user)):
#     """Get all documents for the current user."""
#     try:
#         print("=" * 50)
#         print("DEBUG: get_documents endpoint called")
#         print(f"Current user received: {current_user}")
#         print(f"Current user type: {type(current_user)}")
        
#         # Check if current_user is valid
#         if not current_user:
#             print("ERROR: current_user is None or empty")
#             raise HTTPException(status_code=400, detail="No user information provided")
        
#         # Extract user ID from UserResponse attributes
#         user_id = None
#         if hasattr(current_user, 'id'):
#             user_id = current_user.id
#             print(f"Found user identifier in field 'id': {user_id}")
#         elif hasattr(current_user, 'email'):
#             user_id = current_user.email
#             print(f"Found user identifier in field 'email': {user_id}")
#         else:
#             print(f"ERROR: No user ID found in UserResponse attributes")
#             raise HTTPException(status_code=400, detail="Invalid user token - no user ID found")
        
#         print(f"Using user_id: {user_id}")
        
#         # Test database connection
#         print("Testing database connection...")
#         try:
#             with db_manager.get_connection() as conn:
#                 print(f"Database connection successful: {conn}")
                
#                 with conn.cursor() as cursor:
#                     print("Cursor created successfully")
                    
#                     # Test basic query
#                     cursor.execute("SELECT version()")
#                     version = cursor.fetchone()
#                     print(f"PostgreSQL version: {version[0] if version else 'Unknown'}")
                    
#                     # Check if documents table exists
#                     cursor.execute("""
#                         SELECT EXISTS (
#                             SELECT FROM information_schema.tables 
#                             WHERE table_name = 'documents'
#                         )
#                     """)
#                     table_exists = cursor.fetchone()[0]
#                     print(f"Documents table exists: {table_exists}")
                    
#                     if not table_exists:
#                         print("ERROR: Documents table does not exist!")
#                         raise HTTPException(status_code=500, detail="Documents table not found")
                    
#                     # Check table structure
#                     cursor.execute("""
#                         SELECT column_name, data_type 
#                         FROM information_schema.columns 
#                         WHERE table_name = 'documents'
#                         ORDER BY ordinal_position
#                     """)
#                     columns = cursor.fetchall()
#                     print(f"Documents table columns: {columns}")
                    
#                     # Check total documents count
#                     cursor.execute("SELECT COUNT(*) FROM documents")
#                     total_docs = cursor.fetchone()[0]
#                     print(f"Total documents in database: {total_docs}")
                    
#                     # Check documents for this specific user
#                     cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = %s", (str(user_id),))
#                     user_docs = cursor.fetchone()[0]
#                     print(f"Documents for user {user_id}: {user_docs}")
                    
#                     # Query user's documents with detailed info
#                     query = """
#                         SELECT id, original_filename, file_size, upload_timestamp, mime_type, user_id
#                         FROM documents 
#                         WHERE user_id = %s
#                         ORDER BY upload_timestamp DESC
#                     """
#                     print(f"Executing query: {query} with user_id: {user_id}")
#                     cursor.execute(query, (str(user_id),))
#                     documents = cursor.fetchall()
                    
#                     print(f"Query returned {len(documents)} documents")
                    
#                     # Convert to list of dictionaries
#                     result = []
#                     for i, doc in enumerate(documents):
#                         print(f"Processing document {i+1}: {doc}")
#                         doc_dict = {
#                             "id": doc[0],
#                             "original_filename": doc[1],
#                             "file_size": doc[2],
#                             "upload_date": doc[3].isoformat() if doc[3] else None,
#                             "content_type": doc[4],  # Use 'content_type' in response for API consistency
#                             "user_id": doc[5]  # Include for debugging
#                         }
#                         result.append(doc_dict)
                    
#                     print(f"Final result: {result}")
#                     print("=" * 50)
#                     return {"documents": result, "debug_info": {
#                         "user_id_used": str(user_id),
#                         "total_docs_in_db": total_docs,
#                         "user_docs_count": user_docs
#                     }}
                    
#         except psycopg2.Error as db_error:
#             print(f"DATABASE ERROR: {db_error}")
#             print(f"Error code: {db_error.pgcode if hasattr(db_error, 'pgcode') else 'Unknown'}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
            
#     except HTTPException:
#         # Re-raise HTTP exceptions as-is
#         raise
#     except Exception as e:
#         print(f"UNEXPECTED ERROR: {e}")
#         import traceback
#         print("Full traceback:")
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



##Minio 

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from ..api.auth import get_current_user
from ..core.database import db_manager
from ..schemas.user_schemas import UserResponse
from ..schemas.document_schemas import DocumentResponse, DocumentUploadResponse
from ..services.document_service import document_service
import logging
import psycopg2
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a document for the current user."""
    try:
        print("=" * 50)
        print("DEBUG: upload_document endpoint called")
        print(f"File: {file.filename}, Size: {file.size}, Content-Type: {file.content_type}")
        print(f"Current user: {current_user}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Get user ID
        user_id = None
        if hasattr(current_user, 'id'):
            user_id = str(current_user.id)
        elif hasattr(current_user, 'email'):
            user_id = current_user.email
        else:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        print(f"Using user_id: {user_id}")
        
        # Upload document
        result = await document_service.upload_document(file, user_id)
        
        print(f"Upload result: {result}")
        print("=" * 50)
        
        return {
            "success": True,
            "message": result["message"],
            "document_id": result["document_id"],
            "status": result["status"],
            "file_info": {
                "filename": file.filename,
                "size": result["file_size"],
                "mime_type": result["mime_type"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=dict)
async def get_documents(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all documents for the current user."""
    try:
        print("=" * 50)
        print("DEBUG: get_documents endpoint called")
        print(f"Current user received: {current_user}")
        print(f"Limit: {limit}, Offset: {offset}")
        
        # Check if current_user is valid
        if not current_user:
            print("ERROR: current_user is None or empty")
            raise HTTPException(status_code=400, detail="No user information provided")
        
        # Extract user ID from UserResponse attributes
        user_id = None
        if hasattr(current_user, 'id'):
            user_id = current_user.id
            print(f"Found user identifier in field 'id': {user_id}")
        elif hasattr(current_user, 'email'):
            user_id = current_user.email
            print(f"Found user identifier in field 'email': {user_id}")
        else:
            print(f"ERROR: No user ID found in UserResponse attributes")
            raise HTTPException(status_code=400, detail="Invalid user token - no user ID found")
        
        print(f"Using user_id: {user_id}")
        
        # Test database connection and get documents
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get documents with processing status
                query = """
                    SELECT 
                        d.id, d.original_filename, d.file_size, d.upload_timestamp, 
                        d.mime_type, d.user_id, d.file_path_minio,
                        dp.processing_status, dp.processing_errors
                    FROM documents d
                    LEFT JOIN document_processing dp ON d.id = dp.document_id
                    WHERE d.user_id = %s
                    ORDER BY d.upload_timestamp DESC
                    LIMIT %s OFFSET %s
                """
                print(f"Executing query: {query}")
                cursor.execute(query, (str(user_id), limit, offset))
                documents = cursor.fetchall()
                
                print(f"Query returned {len(documents)} documents")
                
                # Get total count
                cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = %s", (str(user_id),))
                total_count = cursor.fetchone()[0]
                
                # Convert to list of dictionaries
                result = []
                for i, doc in enumerate(documents):
                    print(f"Processing document {i+1}: {doc}")
                    doc_dict = {
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
                    result.append(doc_dict)
                
                print(f"Final result: {result}")
                print("=" * 50)
                
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
        print(f"UNEXPECTED ERROR: {e}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific document by ID."""
    try:
        user_id = str(current_user.id) if hasattr(current_user, 'id') else current_user.email
        
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

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get download URL for a document."""
    try:
        user_id = str(current_user.id) if hasattr(current_user, 'id') else current_user.email
        
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
                download_url = document_service.get_document_download_url(file_path)
                
                return {"download_url": download_url}
                
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
                    "SELECT file_path_minio FROM documents WHERE id = %s AND user_id = %s",
                    (document_id, user_id)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Document not found")
                
                file_path = result[0]
                
                # Delete document
                document_service.delete_document(file_path, document_id)
                
                return {"message": "Document deleted successfully"}
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
