



from fastapi import APIRouter, HTTPException, Depends
from ..api.auth import get_current_user
from ..core.database import db_manager
from ..schemas.user_schemas import UserResponse
import logging
import psycopg2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/")
async def get_documents(current_user: UserResponse = Depends(get_current_user)):
    """Get all documents for the current user."""
    try:
        print("=" * 50)
        print("DEBUG: get_documents endpoint called")
        print(f"Current user received: {current_user}")
        print(f"Current user type: {type(current_user)}")
        
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
        
        # Test database connection
        print("Testing database connection...")
        try:
            with db_manager.get_connection() as conn:
                print(f"Database connection successful: {conn}")
                
                with conn.cursor() as cursor:
                    print("Cursor created successfully")
                    
                    # Test basic query
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()
                    print(f"PostgreSQL version: {version[0] if version else 'Unknown'}")
                    
                    # Check if documents table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'documents'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    print(f"Documents table exists: {table_exists}")
                    
                    if not table_exists:
                        print("ERROR: Documents table does not exist!")
                        raise HTTPException(status_code=500, detail="Documents table not found")
                    
                    # Check table structure
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'documents'
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    print(f"Documents table columns: {columns}")
                    
                    # Check total documents count
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    total_docs = cursor.fetchone()[0]
                    print(f"Total documents in database: {total_docs}")
                    
                    # Check documents for this specific user
                    cursor.execute("SELECT COUNT(*) FROM documents WHERE user_id = %s", (str(user_id),))
                    user_docs = cursor.fetchone()[0]
                    print(f"Documents for user {user_id}: {user_docs}")
                    
                    # Query user's documents with detailed info
                    query = """
                        SELECT id, original_filename, file_size, upload_timestamp, mime_type, user_id
                        FROM documents 
                        WHERE user_id = %s
                        ORDER BY upload_timestamp DESC
                    """
                    print(f"Executing query: {query} with user_id: {user_id}")
                    cursor.execute(query, (str(user_id),))
                    documents = cursor.fetchall()
                    
                    print(f"Query returned {len(documents)} documents")
                    
                    # Convert to list of dictionaries
                    result = []
                    for i, doc in enumerate(documents):
                        print(f"Processing document {i+1}: {doc}")
                        doc_dict = {
                            "id": doc[0],
                            "original_filename": doc[1],
                            "file_size": doc[2],
                            "upload_date": doc[3].isoformat() if doc[3] else None,
                            "content_type": doc[4],  # Use 'content_type' in response for API consistency
                            "user_id": doc[5]  # Include for debugging
                        }
                        result.append(doc_dict)
                    
                    print(f"Final result: {result}")
                    print("=" * 50)
                    return {"documents": result, "debug_info": {
                        "user_id_used": str(user_id),
                        "total_docs_in_db": total_docs,
                        "user_docs_count": user_docs
                    }}
                    
        except psycopg2.Error as db_error:
            print(f"DATABASE ERROR: {db_error}")
            print(f"Error code: {db_error.pgcode if hasattr(db_error, 'pgcode') else 'Unknown'}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")