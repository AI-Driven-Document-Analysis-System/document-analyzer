

# # Import necessary modules for FastAPI web framework
# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel  # For data validation and serialization
# from datetime import datetime   # For timestamp handling
# import logging                  # For application logging
# import traceback               # For detailed error information
# import json                    # For JSON data handling
# from ..services.summarization_service import summarize_with_options, get_summary_options
# from ..core.database import db_manager  # Database connection manager
# from ..api.auth import get_current_user  # Authentication middleware
# from ..schemas.user_schemas import UserResponse  # User data schema
# import psycopg2  # PostgreSQL database driver

# # Set up logging for this module - helps track what happens during execution
# logger = logging.getLogger(__name__)

# # Create an API router with a prefix and tags for organization
# # This groups all summarization-related endpoints under /summarize
# router = APIRouter(prefix="/summarize", tags=["summarization"])

# # Pydantic models define the structure of data coming into and going out of the API
# # These ensure type safety and automatic validation

# class SummarizationRequest(BaseModel):
#     """
#     Defines what data the client must send when requesting a summary.
#     Pydantic automatically validates these fields and their types.
#     """
#     document_id: str      # UUID of the document to summarize
#     summary_type: str     # Which type of summary: "brief", "detailed", "domain_specific"
#     summary_length: int   # Desired word count for the summary

# class SummarizationResponse(BaseModel):
#     """
#     Defines the structure of the response sent back to the client.
#     This ensures consistent API responses and helps with documentation.
#     """
#     success: bool          # Whether the operation was successful
#     document_id: str       # Echo back the document ID
#     document_name: str     # Original filename of the document
#     summary_text: str      # The actual generated summary
#     key_points: list[str] | None  # Optional list of key points (not currently used)
#     word_count: int        # Actual word count of generated summary
#     model_used: str        # Which AI model was used (BART, PEGASUS, T5)
#     summary_type: str      # Human-readable summary type name
#     created_at: str        # ISO timestamp of when summary was generated

# def get_summary_mapping():
#     """
#     Configuration function that maps frontend summary types to AI models.
    
#     This acts as a translation layer between user-friendly names and technical details.
#     Each summary type has different characteristics:
#     - brief: Quick overview using BART (good for concise summaries)
#     - detailed: Comprehensive analysis using Pegasus (better for longer summaries)
#     - domain_specific: Specialized using T5 (can be fine-tuned for specific domains)
    
#     Returns:
#         dict: Mapping of summary types to their configurations
#     """
#     return {
#         "brief": {
#             "model": "bart",                    # BART model for brief summaries
#             "name": "Brief Summary",            # Display name for frontend
#             "max_length": 150,                  # Maximum words for this type
#             "min_length": 50                    # Minimum words for this type
#         },
#         "detailed": {
#             "model": "pegasus",                 # Pegasus model for detailed summaries
#             "name": "Detailed Summary",         # Display name for frontend
#             "max_length": 250,                  # Longer summaries allowed
#             "min_length": 80                    # Higher minimum for more detail
#         },
#         "domain_specific": {
#             "model": "t5",                      # T5 model for specialized summaries
#             "name": "Domain Specific Summary",  # Display name for frontend
#             "max_length": 200,                  # Medium length summaries
#             "min_length": 70                    # Medium minimum requirement
#         }
#     }

# @router.post("/", response_model=SummarizationResponse)
# async def summarize_document(
#     request: SummarizationRequest, 
#     current_user: UserResponse = Depends(get_current_user)
# ):
#     """
#     Main API endpoint for generating document summaries.
    
#     This endpoint:
#     1. Validates the user is authenticated
#     2. Checks if the requested summary type is valid
#     3. Fetches the document from the database
#     4. Generates a summary using the appropriate AI model
#     5. Stores the summary in the database
#     6. Returns the summary to the client
    
#     Args:
#         request: Contains document_id, summary_type, and summary_length
#         current_user: Authenticated user (injected by dependency)
    
#     Returns:
#         SummarizationResponse: The generated summary and metadata
    
#     Raises:
#         HTTPException: For various error conditions (400, 404, 500)
#     """
#     try:
#         # Log the incoming request for debugging purposes
#         logger.info(f"Received summarize request: {request.dict()}")

#         # Get the configuration mapping for different summary types
#         summary_mapping = get_summary_mapping()
        
#         # Validate that the requested summary type is supported
#         if request.summary_type not in summary_mapping:
#             logger.error(f"Invalid summary type: {request.summary_type}")
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Invalid summary type. Available options: {list(summary_mapping.keys())}"
#             )

#         # Fetch document content from the database
#         # We need to verify the document exists and belongs to the current user
#         with db_manager.get_connection() as conn:
#             with conn.cursor() as cursor:
#                 # Complex JOIN query to get document info, content, and classification
#                 # This ensures we have all the data we need in one query
#                 query = """
#                     SELECT d.original_filename, dc.extracted_text, dc_class.document_type
#                     FROM documents d
#                     LEFT JOIN document_content dc ON d.id = dc.document_id
#                     LEFT JOIN document_classifications dc_class ON d.id = dc_class.document_id
#                     WHERE d.id = %s AND d.user_id = %s
#                 """
#                 # Execute with parameterized query to prevent SQL injection
#                 cursor.execute(query, (request.document_id, str(current_user.id)))
#                 result = cursor.fetchone()
                
#                 # Check if document was found and belongs to user
#                 if not result:
#                     raise HTTPException(
#                         status_code=404, 
#                         detail="Document not found or not owned by user"
#                     )
                
#                 # Unpack the query results
#                 document_name, document_content, document_type = result
                
#                 # Verify that the document has extractable text content
#                 if not document_content:
#                     raise HTTPException(
#                         status_code=400, 
#                         detail="No extracted text available for this document"
#                     )

#         # Get the configuration for the requested summary type
#         config = summary_mapping[request.summary_type]
#         model_name = config["model"]
        
#         # Adjust summary parameters based on user's length preference
#         # We respect the model's limits but try to accommodate user preferences
#         config["max_length"] = min(request.summary_length, config["max_length"])
#         config["min_length"] = max(30, request.summary_length // 3)  # At least 1/3 of requested length
        
#         logger.info(f"Generating {request.summary_type} summary using {model_name} model")

#         # Call the AI service to generate the actual summary
#         # This is where the machine learning happens
#         summary_text = summarize_with_options(document_content, config)
        
#         # Calculate actual word count of the generated summary
#         word_count = len(summary_text.split())

#         # Store the generated summary in the database for future reference
#         # This allows users to retrieve summaries later and helps with caching
#         try:
#             with db_manager.get_connection() as conn:
#                 with conn.cursor() as cursor:
#                     query = """
#                         INSERT INTO document_summaries (document_id, summary_text, key_points, model_version, created_at)
#                         VALUES (%s, %s, %s, %s, %s)
#                         RETURNING id
#                     """
#                     cursor.execute(query, (
#                         request.document_id,     # Link to original document
#                         summary_text,            # The generated summary
#                         None,                    # Key points (not implemented yet)
#                         model_name,              # Which model was used
#                         datetime.utcnow()        # When it was created
#                     ))
#                     conn.commit()  # Make sure the data is saved
#         except Exception as db_error:
#             # Log database errors but don't fail the request
#             # The summary was generated successfully, storing it is a bonus
#             logger.error(f"Failed to store summary in database: {str(db_error)}")

#         # Build the response object with all the required information
#         response = SummarizationResponse(
#             success=True,                        # Indicate successful operation
#             document_id=request.document_id,     # Echo back the document ID
#             document_name=document_name,         # Original filename
#             summary_text=summary_text,           # The actual summary
#             key_points=None,                     # Not implemented yet
#             word_count=word_count,               # Actual words in summary
#             model_used=model_name.upper(),       # Model name in uppercase
#             summary_type=config["name"],         # Human-readable type name
#             created_at=datetime.utcnow().isoformat()  # ISO timestamp
#         )

#         logger.info(f"Summary generated successfully using {model_name}")
#         return response

#     except HTTPException as e:
#         # Re-raise HTTP exceptions (these are expected errors with proper status codes)
#         raise
#     except Exception as e:
#         # Catch any unexpected errors and convert them to HTTP 500 errors
#         logger.error(f"Error generating summary: {str(e)}")
#         logger.error(traceback.format_exc())  # Log full stack trace for debugging
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Failed to generate summary: {str(e)}"
#         )

# @router.get("/options")
# async def get_available_summary_options():
#     """
#     Endpoint to get available summarization options.
    
#     This allows the frontend to dynamically discover what summary types
#     are available without hardcoding them. Useful for configuration
#     and building dynamic user interfaces.
    
#     Returns:
#         dict: Success status and available options with their configurations
#     """
#     try:
#         # Get the current summary type mapping
#         mapping = get_summary_mapping()
        
#         # Return success response with options
#         return {
#             "success": True,
#             "options": mapping
#         }
#     except Exception as e:
#         # Handle any errors in getting options
#         logger.error(f"Error getting summary options: {str(e)}")
#         raise HTTPException(
#             status_code=500, 
#             detail="Failed to get summary options"
#         )

# # Key architectural patterns explained:

# # 1. DEPENDENCY INJECTION:
# #    - get_current_user is injected as a dependency
# #    - This handles authentication automatically for protected endpoints
# #    - FastAPI calls this function before the main endpoint function

# # 2. DATABASE TRANSACTIONS:
# #    - Uses context managers (with statements) for database connections
# #    - Automatically handles connection cleanup and error handling
# #    - Parameterized queries prevent SQL injection attacks

# # 3. ERROR HANDLING LAYERS:
# #    - HTTPException for expected errors with proper HTTP status codes
# #    - Generic Exception catching for unexpected errors
# #    - Detailed logging for debugging while not exposing internals to users

# # 4. DATA VALIDATION:
# #    - Pydantic models automatically validate input and output data
# #    - Type hints provide IDE support and runtime checking
# #    - Automatic API documentation generation

# # 5. SEPARATION OF CONCERNS:
# #    - API layer handles HTTP requests/responses
# #    - Service layer (summarization_service) handles business logic
# #    - Database layer handles data persistence
# #    - Each layer has a specific responsibility


# Import necessary modules for FastAPI web framework
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel  # For data validation and serialization
from datetime import datetime   # For timestamp handling
import logging                  # For application logging
import traceback               # For detailed error information
import json                    # For JSON data handling
from ..services.summarization_service import summarize_with_options, get_summary_options
from ..core.database import db_manager  # Database connection manager
from ..api.auth import get_current_user  # Authentication middleware
from ..schemas.user_schemas import UserResponse  # User data schema
import psycopg2  # PostgreSQL database driver

# Set up logging for this module - helps track what happens during execution
logger = logging.getLogger(__name__)

# Create an API router with a prefix and tags for organization
# This groups all summarization-related endpoints under /summarize
router = APIRouter(prefix="/summarize", tags=["summarization"])

# Pydantic models define the structure of data coming into and going out of the API
# These ensure type safety and automatic validation

class SummarizationRequest(BaseModel):
    """
    Defines what data the client must send when requesting a summary.
    Pydantic automatically validates these fields and their types.
    """
    document_id: str      # UUID of the document to summarize
    summary_type: str     # Which type of summary: "brief", "detailed", "domain_specific"
    summary_length: int   # Desired word count for the summary

class SummarizationResponse(BaseModel):
    """
    Defines the structure of the response sent back to the client.
    This ensures consistent API responses and helps with documentation.
    """
    success: bool          # Whether the operation was successful
    document_id: str       # Echo back the document ID
    document_name: str     # Original filename of the document
    summary_text: str      # The actual generated summary
    key_points: list[str] | None  # Optional list of key points (not currently used)
    word_count: int        # Actual word count of generated summary
    model_used: str        # Which AI model was used (BART, PEGASUS, T5)
    summary_type: str      # Human-readable summary type name
    created_at: str        # ISO timestamp of when summary was generated
    from_cache: bool       # Indicates if summary was retrieved from cache

def get_summary_mapping():
    """
    Configuration function that maps frontend summary types to AI models.
    
    This acts as a translation layer between user-friendly names and technical details.
    Each summary type has different characteristics:
    - brief: Quick overview using BART (good for concise summaries)
    - detailed: Comprehensive analysis using Pegasus (better for longer summaries)
    - domain_specific: Specialized using T5 (can be fine-tuned for specific domains)
    
    Returns:
        dict: Mapping of summary types to their configurations
    """
    return {
        "brief": {
            "model": "bart",                    # BART model for brief summaries
            "name": "Brief Summary",            # Display name for frontend
            "max_length": 150,                  # Maximum words for this type
            "min_length": 50                    # Minimum words for this type
        },
        "detailed": {
            "model": "pegasus",                 # Pegasus model for detailed summaries
            "name": "Detailed Summary",         # Display name for frontend
            "max_length": 250,                  # Longer summaries allowed
            "min_length": 80                    # Higher minimum for more detail
        },
        "domain_specific": {
            "model": "t5",                      # T5 model for specialized summaries
            "name": "Domain Specific Summary",  # Display name for frontend
            "max_length": 200,                  # Medium length summaries
            "min_length": 70                    # Medium minimum requirement
        }
    }

def calculate_word_count(text: str) -> int:
    """
    Calculate the word count of a text string.
    
    Args:
        text: The text to count words in
        
    Returns:
        int: Number of words in the text
    """
    if not text or not text.strip():
        return 0
    return len(text.strip().split())

def check_existing_summary(document_id: str, model_name: str, target_word_count: int, tolerance: int = 20):
    """
    Check if a similar summary already exists in the database.
    
    Args:
        document_id: UUID of the document
        model_name: The model used for summarization
        target_word_count: Desired word count
        tolerance: Acceptable word count difference (default: ±20 words)
        
    Returns:
        dict or None: Existing summary data if found, None otherwise
    """
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Query to find existing summaries with similar word count
                query = """
                    SELECT id, summary_text, key_points, model_version, created_at,
                           LENGTH(summary_text) - LENGTH(REPLACE(summary_text, ' ', '')) + 1 as word_count
                    FROM document_summaries
                    WHERE document_id = %s AND model_version = %s
                    HAVING ABS((LENGTH(summary_text) - LENGTH(REPLACE(summary_text, ' ', '')) + 1) - %s) <= %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor.execute(query, (document_id, model_name, target_word_count, tolerance))
                result = cursor.fetchone()
                
                if result:
                    summary_id, summary_text, key_points, model_version, created_at, word_count = result
                    return {
                        'id': summary_id,
                        'summary_text': summary_text,
                        'key_points': key_points,
                        'model_version': model_version,
                        'created_at': created_at,
                        'word_count': word_count
                    }
                return None
                
    except Exception as e:
        logger.error(f"Error checking existing summary: {str(e)}")
        return None

@router.post("/", response_model=SummarizationResponse)
async def summarize_document(
    request: SummarizationRequest, 
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Main API endpoint for generating document summaries.
    
    This endpoint:
    1. Validates the user is authenticated
    2. Checks if the requested summary type is valid
    3. Checks for existing cached summary with similar word count
    4. If no cache hit, fetches the document from the database
    5. Generates a summary using the appropriate AI model
    6. Stores the summary in the database
    7. Returns the summary to the client
    
    Args:
        request: Contains document_id, summary_type, and summary_length
        current_user: Authenticated user (injected by dependency)
    
    Returns:
        SummarizationResponse: The generated summary and metadata
    
    Raises:
        HTTPException: For various error conditions (400, 404, 500)
    """
    try:
        # Log the incoming request for debugging purposes
        logger.info(f"Received summarize request: {request.dict()}")

        # Get the configuration mapping for different summary types
        summary_mapping = get_summary_mapping()
        
        # Validate that the requested summary type is supported
        if request.summary_type not in summary_mapping:
            logger.error(f"Invalid summary type: {request.summary_type}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid summary type. Available options: {list(summary_mapping.keys())}"
            )

        # Get the configuration for the requested summary type
        config = summary_mapping[request.summary_type]
        model_name = config["model"]

        # First, check if we already have a cached summary with similar word count
        logger.info(f"Checking for existing summary with model {model_name} and target word count {request.summary_length}")
        existing_summary = check_existing_summary(request.document_id, model_name, request.summary_length)
        
        if existing_summary:
            logger.info(f"Found existing summary with {existing_summary['word_count']} words, returning from cache")
            
            # Fetch document name for the response
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT original_filename FROM documents WHERE id = %s AND user_id = %s"
                    cursor.execute(query, (request.document_id, str(current_user.id)))
                    result = cursor.fetchone()
                    
                    if not result:
                        raise HTTPException(
                            status_code=404, 
                            detail="Document not found or not owned by user"
                        )
                    
                    document_name = result[0]

            # Return the cached summary
            response = SummarizationResponse(
                success=True,
                document_id=request.document_id,
                document_name=document_name,
                summary_text=existing_summary['summary_text'],
                key_points=existing_summary['key_points'],
                word_count=existing_summary['word_count'],
                model_used=model_name.upper(),
                summary_type=config["name"],
                created_at=existing_summary['created_at'].isoformat() if existing_summary['created_at'] else datetime.utcnow().isoformat(),
                from_cache=True
            )
            return response

        # No cached summary found, proceed with generation
        logger.info(f"No suitable cached summary found, generating new summary")

        # Fetch document content from the database
        # We need to verify the document exists and belongs to the current user
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Complex JOIN query to get document info, content, and classification
                # This ensures we have all the data we need in one query
                query = """
                    SELECT d.original_filename, dc.extracted_text, dc_class.document_type
                    FROM documents d
                    LEFT JOIN document_content dc ON d.id = dc.document_id
                    LEFT JOIN document_classifications dc_class ON d.id = dc_class.document_id
                    WHERE d.id = %s AND d.user_id = %s
                """
                # Execute with parameterized query to prevent SQL injection
                cursor.execute(query, (request.document_id, str(current_user.id)))
                result = cursor.fetchone()
                
                # Check if document was found and belongs to user
                if not result:
                    raise HTTPException(
                        status_code=404, 
                        detail="Document not found or not owned by user"
                    )
                
                # Unpack the query results
                document_name, document_content, document_type = result
                
                # Verify that the document has extractable text content
                if not document_content:
                    raise HTTPException(
                        status_code=400, 
                        detail="No extracted text available for this document"
                    )

        # Adjust summary parameters based on user's length preference
        # We respect the model's limits but try to accommodate user preferences
        config["max_length"] = min(request.summary_length, config["max_length"])
        config["min_length"] = max(30, request.summary_length // 3)  # At least 1/3 of requested length
        
        logger.info(f"Generating {request.summary_type} summary using {model_name} model")

        # Call the AI service to generate the actual summary
        # This is where the machine learning happens
        summary_text = summarize_with_options(document_content, config)
        
        # Calculate actual word count of the generated summary
        word_count = calculate_word_count(summary_text)

        # Store the generated summary in the database for future reference
        # This allows users to retrieve summaries later and helps with caching
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO document_summaries (document_id, summary_text, key_points, model_version, word_count, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    cursor.execute(query, (
                        request.document_id,     # Link to original document
                        summary_text,            # The generated summary
                        None,                    # Key points (not implemented yet)
                        model_name,              # Which model was used
                        word_count,              # Calculated word count
                        datetime.utcnow()        # When it was created
                    ))
                    conn.commit()  # Make sure the data is saved
                    logger.info(f"Summary stored in database with word count: {word_count}")
        except Exception as db_error:
            # Log database errors but don't fail the request
            # The summary was generated successfully, storing it is a bonus
            logger.error(f"Failed to store summary in database: {str(db_error)}")

        # Build the response object with all the required information
        response = SummarizationResponse(
            success=True,                        # Indicate successful operation
            document_id=request.document_id,     # Echo back the document ID
            document_name=document_name,         # Original filename
            summary_text=summary_text,           # The actual summary
            key_points=None,                     # Not implemented yet
            word_count=word_count,               # Actual words in summary
            model_used=model_name.upper(),       # Model name in uppercase
            summary_type=config["name"],         # Human-readable type name
            created_at=datetime.utcnow().isoformat(),  # ISO timestamp
            from_cache=False                     # Indicates this is newly generated
        )

        logger.info(f"Summary generated successfully using {model_name} with {word_count} words")
        return response

    except HTTPException as e:
        # Re-raise HTTP exceptions (these are expected errors with proper status codes)
        raise
    except Exception as e:
        # Catch any unexpected errors and convert them to HTTP 500 errors
        logger.error(f"Error generating summary: {str(e)}")
        logger.error(traceback.format_exc())  # Log full stack trace for debugging
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate summary: {str(e)}"
        )

@router.get("/options")
async def get_available_summary_options():
    """
    Endpoint to get available summarization options.
    
    This allows the frontend to dynamically discover what summary types
    are available without hardcoding them. Useful for configuration
    and building dynamic user interfaces.
    
    Returns:
        dict: Success status and available options with their configurations
    """
    try:
        # Get the current summary type mapping
        mapping = get_summary_mapping()
        
        # Return success response with options
        return {
            "success": True,
            "options": mapping
        }
    except Exception as e:
        # Handle any errors in getting options
        logger.error(f"Error getting summary options: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get summary options"
        )

# Key architectural patterns explained:

# 1. CACHING STRATEGY:
#    - check_existing_summary() looks for summaries with similar word counts
#    - Uses a tolerance parameter (±20 words by default) for flexibility
#    - Returns cached results immediately if found, avoiding expensive AI processing

# 2. WORD COUNT CALCULATION:
#    - calculate_word_count() provides consistent word counting logic
#    - SQL query uses LENGTH functions to calculate word count in database
#    - Word count is now stored in database for efficient lookups

# 3. DATABASE SCHEMA UPDATE REQUIRED:
#    - ALTER TABLE document_summaries ADD COLUMN word_count INTEGER;
#    - This allows efficient querying of summaries by word count

# 4. DEPENDENCY INJECTION:
#    - get_current_user is injected as a dependency
#    - This handles authentication automatically for protected endpoints

# 5. ERROR HANDLING LAYERS:
#    - Cache lookup failures don't break the main flow
#    - HTTPException for expected errors with proper HTTP status codes
#    - Generic Exception catching for unexpected errors

# 6. PERFORMANCE OPTIMIZATION:
#    - Cached summaries avoid expensive AI model inference
#    - Single database query for cache lookup
#    - Efficient word count calculation using SQL functions

