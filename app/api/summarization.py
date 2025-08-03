# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel
# from datetime import datetime
# import logging
# from ..services.summarization_service import summarize_with_options, get_summary_options
# from ..core.database import db_manager
# from ..api.auth import get_current_user
# import psycopg2

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/summarize", tags=["summarization"])

# class SummarizationRequest(BaseModel):
#     document_id: str
#     model_name: str
#     summary_type: str
#     summary_length: int

# class SummarizationResponse(BaseModel):
#     success: bool
#     document_id: str
#     document_name: str
#     summary_text: str
#     key_points: list[str] | None
#     word_count: int
#     model_used: str
#     summary_type: str
#     created_at: str

# @router.post("/", response_model=SummarizationResponse)
# async def summarize_document(request: SummarizationRequest, current_user: dict = Depends(get_current_user)):
#     """Generate a summary for the specified document."""
#     try:
#         # Map frontend summary types to backend summary options
#         summary_type_mapping = {
#             "brief": "1",
#             "detailed": "2",
#             "key-points": "5",
#             "technical": "3",
#             "business": "4"
#         }

#         if request.summary_type not in summary_type_mapping:
#             raise HTTPException(status_code=400, detail="Invalid summary type")

#         options = get_summary_options()
#         selected_option = options.get(summary_type_mapping[request.summary_type])
#         if not selected_option:
#             raise HTTPException(status_code=400, detail="Invalid summary option")

#         # Fetch document content from database
#         with db_manager.get_connection() as conn:
#             with conn.cursor() as cursor:
#                 query = """
#                     SELECT d.original_filename, dc.extracted_text
#                     FROM documents d
#                     LEFT JOIN document_content dc ON d.id = dc.document_id
#                     WHERE d.id = %s AND d.user_id = %s
#                 """
#                 cursor.execute(query, (request.document_id, str(current_user["user_id"])))
#                 result = cursor.fetchone()
#                 if not result:
#                     raise HTTPException(status_code=404, detail="Document not found or not owned by user")
                
#                 document_name, document_content = result
#                 if not document_content:
#                     raise HTTPException(status_code=400, detail="No extracted text available for this document")

#         # Update summary parameters
#         selected_option["max_length"] = request.summary_length
#         selected_option["min_length"] = max(30, request.summary_length // 2)

#         # Generate summary
#         summary_text = summarize_with_options(document_content, selected_option)

#         # Extract key points
#         key_points = []
#         if selected_option["name"] == "Key Points Only":
#             key_points = [line.strip() for line in summary_text.split("\n") if line.strip() and not line.startswith("Chunk")]

#         # Calculate word count
#         word_count = len(summary_text.split())

#         # Store summary in document_summaries table
#         with db_manager.get_connection() as conn:
#             with conn.cursor() as cursor:
#                 query = """
#                     INSERT INTO document_summaries (document_id, summary_text, key_points, model_version, created_at)
#                     VALUES (%s, %s, %s, %s, %s)
#                     RETURNING id
#                 """
#                 cursor.execute(query, (
#                     request.document_id,
#                     summary_text,
#                     key_points if key_points else None,
#                     request.model_name,
#                     datetime.utcnow()
#                 ))
#                 conn.commit()

#         # Prepare response
#         response = SummarizationResponse(
#             success=True,
#             document_id=request.document_id,
#             document_name=document_name,
#             summary_text=summary_text,
#             key_points=key_points if key_points else None,
#             word_count=word_count,
#             model_used=request.model_name,
#             summary_type=selected_option["name"],
#             created_at=datetime.utcnow().isoformat()
#         )

#         logger.info(f"Summary generated for document_id: {request.document_id}")
#         return response

#     except psycopg2.Error as e:
#         logger.error(f"Database error: {e}")
#         raise HTTPException(status_code=500, detail="Database error")
#     except Exception as e:
#         logger.error(f"Error generating summary: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import logging
import traceback
import json
from ..services.summarization_service import summarize_with_options, get_summary_options
from ..core.database import db_manager
from ..api.auth import get_current_user
from ..schemas.user_schemas import UserResponse
import psycopg2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summarize", tags=["summarization"])

class SummarizationRequest(BaseModel):
    document_id: str
    model_name: str
    summary_type: str  # Now expects "1", "2", "3", "4"
    summary_length: int

class SummarizationResponse(BaseModel):
    success: bool
    document_id: str
    document_name: str
    summary_text: str
    key_points: list[str] | None
    word_count: int
    model_used: str
    summary_type: str
    created_at: str

@router.post("/", response_model=SummarizationResponse)
async def summarize_document(request: SummarizationRequest, current_user: UserResponse = Depends(get_current_user)):
    """Generate a summary for the specified document."""
    try:
        logger.info(f"Received summarize request: {request.dict()}")
        logger.info(f"Current user: {current_user.dict()}")

        # Get available summary options
        options = get_summary_options()
        
        # Validate summary type - now expects "1", "2", "3", "4"
        if request.summary_type not in options:
            logger.error(f"Invalid summary type: {request.summary_type}")
            logger.error(f"Available options: {list(options.keys())}")
            raise HTTPException(status_code=400, detail=f"Invalid summary type. Available options: {list(options.keys())}")

        selected_option = options[request.summary_type]
        logger.info(f"Selected summary option: {selected_option}")

        # Fetch document content from database
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT d.original_filename, dc.extracted_text
                    FROM documents d
                    LEFT JOIN document_content dc ON d.id = dc.document_id
                    WHERE d.id = %s AND d.user_id = %s
                """
                logger.debug(f"Executing query: {cursor.mogrify(query, (request.document_id, str(current_user.id))).decode()}")
                cursor.execute(query, (request.document_id, str(current_user.id)))
                result = cursor.fetchone()
                if not result:
                    logger.error(f"Document not found or not owned by user: document_id={request.document_id}, user_id={current_user.id}")
                    raise HTTPException(status_code=404, detail="Document not found or not owned by user")
                
                document_name, document_content = result
                if not document_content:
                    logger.error(f"No extracted text for document_id={request.document_id}")
                    raise HTTPException(status_code=400, detail="No extracted text available for this document")

        # Create a copy of selected_option to avoid modifying the original
        summary_options = selected_option.copy()
        
        # Update summary parameters based on request (only for non-Key Points types)
        if selected_option["name"] != "Key Points":
            summary_options["max_length"] = min(request.summary_length, 300)  # Cap at 300
            summary_options["min_length"] = max(30, request.summary_length // 3)  # Minimum 30 words
        
        logger.info(f"Final summary options: {summary_options}")

        # Generate summary
        logger.info(f"Generating summary for document: {document_name}")
        summary_text = summarize_with_options(document_content, summary_options)
        
        # Extract key points if it's Key Points type
        key_points = []
        if selected_option["name"] == "Key Points":
            # For Key Points, the summary_text contains formatted bullet points
            # Extract clean bullet points for the key_points field
            lines = summary_text.split("\n")
            for line in lines:
                clean_line = line.strip()
                if clean_line and clean_line.startswith("• "):
                    # Remove bullet point and clean up
                    key_point = clean_line[2:].strip()
                    if key_point and not key_point.startswith("=") and not key_point.startswith("KEY POINTS"):
                        key_points.append(key_point)
            logger.info(f"Extracted {len(key_points)} key points")

        # Calculate word count (approximate, excluding formatting)
        # Remove formatting characters for more accurate word count
        clean_text = summary_text.replace("=", "").replace("📋", "").replace("📖", "").replace("🔑", "").replace("💼", "")
        word_count = len([word for word in clean_text.split() if word.strip()])
        logger.info(f"Summary word count: {word_count}")

        # Store summary in document_summaries table
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO document_summaries (document_id, summary_text, key_points, model_version, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    # Convert key_points to JSON string for jsonb column
                    key_points_json = json.dumps(key_points) if key_points else None
                    logger.debug(f"Storing summary in database...")
                    cursor.execute(query, (
                        request.document_id,
                        summary_text,
                        key_points_json,
                        request.model_name,
                        datetime.utcnow()
                    ))
                    summary_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Summary stored with ID: {summary_id}")
        except Exception as db_error:
            logger.error(f"Failed to store summary in database: {str(db_error)}")
            # Continue anyway - we still have the summary to return

        # Prepare response
        response = SummarizationResponse(
            success=True,
            document_id=request.document_id,
            document_name=document_name,
            summary_text=summary_text,
            key_points=key_points if key_points else None,
            word_count=word_count,
            model_used=request.model_name,
            summary_type=selected_option["name"],
            created_at=datetime.utcnow().isoformat()
        )

        logger.info(f"Summary generated successfully for document_id: {request.document_id}, type: {selected_option['name']}")
        return response

    except HTTPException as e:
        logger.error(f"HTTP exception: {str(e)}")
        raise  # Re-raise HTTPException as-is
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(f"Error code: {e.pgcode if hasattr(e, 'pgcode') else 'Unknown'}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating summary: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

# Optional: Add an endpoint to get available summary options
@router.get("/options")
async def get_available_summary_options():
    """Get available summarization options."""
    try:
        options = get_summary_options()
        return {
            "success": True,
            "options": options
        }
    except Exception as e:
        logger.error(f"Error getting summary options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get summary options")