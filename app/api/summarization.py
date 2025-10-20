
# # Import necessary modules for FastAPI web framework
# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel  # For data validation and serialization
# from datetime import datetime   # For timestamp handling
# import logging                  # For application logging
# import traceback               # For detailed error information
# import json                    # For JSON data handling
# from ..services.summarization_service import summarize_with_options, get_summary_options
# from ..core.database import db_manager  # Database connection manager
# from ..core.dependencies import get_current_user  # Authentication middleware
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
#     from_cache: bool       # Indicates if summary was retrieved from cache

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
#             "name": "Brief Summary"             # Display name for frontend
#         },
#         "detailed": {
#             "model": "pegasus",                 # Pegasus model for detailed summaries
#             "name": "Detailed Summary"          # Display name for frontend
#         },
#         "domain_specific": {
#             "model": "t5",                      # T5 model for specialized summaries
#             "name": "Domain Specific Summary"   # Display name for frontend
#         }
#     }

# def calculate_word_count(text: str) -> int:
#     """
#     Calculate the word count of a text string.
    
#     Args:
#         text: The text to count words in
        
#     Returns:
#         int: Number of words in the text
#     """
#     if not text or not text.strip():
#         return 0
#     return len(text.strip().split())

# def check_existing_summary(document_id: str, model_name: str):
#     """
#     Check if a summary already exists for this document and model combination.
    
#     Args:
#         document_id: UUID of the document
#         model_name: The model used for summarization
        
#     Returns:
#         dict or None: Existing summary data if found, None otherwise
#     """
#     try:
#         with db_manager.get_connection() as conn:
#             with conn.cursor() as cursor:
#                 # Query to find existing summary for this document and model
#                 query = """
#                     SELECT id, summary_text, key_points, model_version, created_at,
#                            LENGTH(summary_text) - LENGTH(REPLACE(summary_text, ' ', '')) + 1 as word_count
#                     FROM document_summaries
#                     WHERE document_id = %s AND model_version = %s
#                     ORDER BY created_at DESC
#                     LIMIT 1
#                 """
#                 cursor.execute(query, (document_id, model_name))
#                 result = cursor.fetchone()
                
#                 if result:
#                     summary_id, summary_text, key_points, model_version, created_at, word_count = result
#                     return {
#                         'id': summary_id,
#                         'summary_text': summary_text,
#                         'key_points': key_points,
#                         'model_version': model_version,
#                         'created_at': created_at,
#                         'word_count': word_count
#                     }
#                 return None
                
#     except Exception as e:
#         logger.error(f"Error checking existing summary: {str(e)}")
#         return None

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
#     3. Checks for existing cached summary for this document and model
#     4. If no cache hit, fetches the document from the database
#     5. Generates a summary using the appropriate AI model
#     6. Stores the summary in the database
#     7. Returns the summary to the client
    
#     Args:
#         request: Contains document_id and summary_type
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

#         # Get the configuration for the requested summary type
#         config = summary_mapping[request.summary_type]
#         model_name = config["model"]

#         # First, check if we already have a cached summary for this document and model
#         logger.info(f"Checking for existing summary with model {model_name}")
#         existing_summary = check_existing_summary(request.document_id, model_name)
        
#         if existing_summary:
#             logger.info(f"Found existing summary with {existing_summary['word_count']} words, returning from cache")
            
#             # Fetch document name for the response
#             with db_manager.get_connection() as conn:
#                 with conn.cursor() as cursor:
#                     query = "SELECT original_filename FROM documents WHERE id = %s AND user_id = %s"
#                     cursor.execute(query, (request.document_id, str(current_user.id)))
#                     result = cursor.fetchone()
                    
#                     if not result:
#                         raise HTTPException(
#                             status_code=404, 
#                             detail="Document not found or not owned by user"
#                         )
                    
#                     document_name = result[0]

#             # Return the cached summary
#             response = SummarizationResponse(
#                 success=True,
#                 document_id=request.document_id,
#                 document_name=document_name,
#                 summary_text=existing_summary['summary_text'],
#                 key_points=existing_summary['key_points'],
#                 word_count=existing_summary['word_count'],
#                 model_used=model_name.upper(),
#                 summary_type=config["name"],
#                 created_at=existing_summary['created_at'].isoformat() if existing_summary['created_at'] else datetime.utcnow().isoformat(),
#                 from_cache=True
#             )
#             return response

#         # No cached summary found, proceed with generation
#         logger.info(f"No cached summary found, generating new summary")

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

#         logger.info(f"Generating {request.summary_type} summary using {model_name} model")

#         # Call the AI service to generate the actual summary
#         # This is where the machine learning happens
#         summary_text = summarize_with_options(document_content, config)
        
#         # Calculate actual word count of the generated summary
#         word_count = calculate_word_count(summary_text)

#         # Store the generated summary in the database for future reference
#         # This allows users to retrieve summaries later and helps with caching
#         try:
#             with db_manager.get_connection() as conn:
#                 with conn.cursor() as cursor:
#                     query = """
#                         INSERT INTO document_summaries (document_id, summary_text, key_points, model_version, word_count, created_at)
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                         RETURNING id
#                     """
#                     cursor.execute(query, (
#                         request.document_id,     # Link to original document
#                         summary_text,            # The generated summary
#                         None,                    # Key points (not implemented yet)
#                         model_name,              # Which model was used
#                         word_count,              # Calculated word count
#                         datetime.utcnow()        # When it was created
#                     ))
#                     conn.commit()  # Make sure the data is saved
#                     logger.info(f"Summary stored in database with word count: {word_count}")
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
#             created_at=datetime.utcnow().isoformat(),  # ISO timestamp
#             from_cache=False                     # Indicates this is newly generated
#         )

#         logger.info(f"Summary generated successfully using {model_name} with {word_count} words")
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

# # Key changes made:

# # 1. REMOVED WORD COUNT CONSTRAINTS:
# #    - Removed summary_length from SummarizationRequest
# #    - Removed max_length and min_length from summary configurations
# #    - Removed word count tolerance from check_existing_summary()

# # 2. SIMPLIFIED CACHING:
# #    - check_existing_summary() now only checks document_id and model_version
# #    - No word count comparison or tolerance calculations
# #    - Returns the most recent summary for the document+model combination

# # 3. UPDATED CONFIGURATION:
# #    - get_summary_mapping() only contains model and name fields
# #    - Removed length-related parameters that constrained AI output

# # 4. CLEANER API CONTRACT:
# #    - Request only needs document_id and summary_type
# #    - AI models can generate summaries of their natural optimal length
# #    - No artificial constraints on summary length

# # 5. IMPROVED CACHING LOGIC:
# #    - If a summary exists for document+model, return it immediately
# #    - Only generate new summary if no existing one found
# #    - Much simpler and more reliable caching strategy



##Worked 

# Import necessary modules for FastAPI web framework
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel  # For data validation and serialization
from datetime import datetime   # For timestamp handling
import logging                  # For application logging
import traceback               # For detailed error information
import json                    # For JSON data handling
from ..services.summarization_service import summarize_with_options, get_summary_options
from ..core.database import db_manager  # Database connection manager
from ..core.dependencies import get_current_user  # Authentication middleware
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
    document_type: str | None  # Document type for domain-specific summaries
    created_at: str        # ISO timestamp of when summary was generated
    from_cache: bool       # Indicates if summary was retrieved from cache

def get_domain_specific_model_mapping():
    """
    Configuration function that maps document types to specific AI models.
    
    This mapping determines which model to use for domain-specific summaries
    based on the document type stored in the database.
    
    Returns:
        dict: Mapping of document types to their optimal models
    """
    return {
        "medical report": "facebook/bart-large-cnn",
        "legal docs": "facebook/bart-large-cnn", 
        "financial docs": "facebook/bart-large-cnn",
        "invoices": "facebook/bart-large-cnn",
        "research paper": "google/pegasus-xsum",
        "letters": "t5-small",
        "news": "google/pegasus-cnn_dailymail"
    }

def get_summary_mapping():
    """
    Configuration function that maps frontend summary types to AI models.
    
    This acts as a translation layer between user-friendly names and technical details.
    Each summary type has different characteristics:
    - brief: Quick overview using BART (good for concise summaries)
    - detailed: Comprehensive analysis using Pegasus (better for longer summaries)
    - domain_specific: Specialized using model based on document type
    
    Returns:
        dict: Mapping of summary types to their configurations
    """
    return {
        "brief": {
            "model": "bart",                    # BART model for brief summaries
            "name": "Brief Summary"             # Display name for frontend
        },
        "detailed": {
            "model": "pegasus",                 # Pegasus model for detailed summaries
            "name": "Detailed Summary"          # Display name for frontend
        },
        "domain_specific": {
            "model": "domain_specific",         # Will be resolved based on document type
            "name": "Domain Specific Summary"   # Display name for frontend
        }
    }

def get_document_type_from_db(document_id: str, user_id: str):
    """
    Fetch the document type from the database for domain-specific summaries.
    
    Args:
        document_id: UUID of the document
        user_id: UUID of the user (for security)
        
    Returns:
        tuple: (document_type, document_name, document_content) or raises exception
    """
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Query to get document info including classification
                query = """
                    SELECT d.original_filename, dc.extracted_text, dc_class.document_type
                    FROM documents d
                    LEFT JOIN document_content dc ON d.id = dc.document_id
                    LEFT JOIN document_classifications dc_class ON d.id = dc_class.document_id
                    WHERE d.id = %s AND d.user_id = %s
                """
                cursor.execute(query, (document_id, user_id))
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(
                        status_code=404, 
                        detail="Document not found or not owned by user"
                    )
                
                document_name, document_content, document_type = result
                
                if not document_content:
                    raise HTTPException(
                        status_code=400, 
                        detail="No extracted text available for this document"
                    )
                
                return document_type, document_name, document_content
                
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error fetching document type from database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch document information"
        )

def resolve_domain_specific_model(document_type: str):
    """
    Resolve the appropriate model for domain-specific summarization.
    
    Args:
        document_type: The type of document from database classification
        
    Returns:
        str: The model identifier to use for summarization
    """
    domain_mapping = get_domain_specific_model_mapping()
    
    # Convert document_type to lowercase for case-insensitive matching
    if document_type:
        document_type_lower = document_type.lower()
        
        # Try exact match first
        if document_type_lower in domain_mapping:
            return domain_mapping[document_type_lower]
        
        # Try partial matches for flexibility
        for doc_type, model in domain_mapping.items():
            if doc_type in document_type_lower or document_type_lower in doc_type:
                return model
    
    # Default fallback model if no specific mapping found
    logger.warning(f"No specific model found for document type: {document_type}, using default BART")
    return "facebook/bart-large-cnn"

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

def check_existing_summary(document_id: str, model_name: str):
    """
    Check if a summary already exists for this document and model combination.
    
    Args:
        document_id: UUID of the document
        model_name: The model used for summarization
        
    Returns:
        dict or None: Existing summary data if found, None otherwise
    """
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Query to find existing summary for this document and model
                query = """
                    SELECT id, summary_text, key_points, model_version, created_at,
                           LENGTH(summary_text) - LENGTH(REPLACE(summary_text, ' ', '')) + 1 as word_count
                    FROM document_summaries
                    WHERE document_id = %s AND model_version = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor.execute(query, (document_id, model_name))
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
    3. For domain_specific summaries, fetches document type from database
    4. Resolves the appropriate model based on document type
    5. Checks for existing cached summary for this document and model
    6. If no cache hit, generates a summary using the appropriate AI model
    7. Stores the summary in the database
    8. Returns the summary to the client
    
    Args:
        request: Contains document_id and summary_type
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
        document_type = None

        # Special handling for domain-specific summaries
        if request.summary_type == "domain_specific":
            # Fetch document type from database
            document_type, document_name, document_content = get_document_type_from_db(
                request.document_id, str(current_user.id)
            )
            
            # Resolve the specific model based on document type
            resolved_model = resolve_domain_specific_model(document_type)
            model_name = resolved_model
            
            logger.info(f"Domain-specific summary: Document type '{document_type}' mapped to model '{model_name}'")
        else:
            # For non-domain-specific summaries, fetch document normally
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT d.original_filename, dc.extracted_text, dc_class.document_type
                        FROM documents d
                        LEFT JOIN document_content dc ON d.id = dc.document_id
                        LEFT JOIN document_classifications dc_class ON d.id = dc_class.document_id
                        WHERE d.id = %s AND d.user_id = %s
                    """
                    cursor.execute(query, (request.document_id, str(current_user.id)))
                    result = cursor.fetchone()
                    
                    if not result:
                        raise HTTPException(
                            status_code=404, 
                            detail="Document not found or not owned by user"
                        )
                    
                    document_name, document_content, document_type = result
                    
                    if not document_content:
                        raise HTTPException(
                            status_code=400, 
                            detail="No extracted text available for this document"
                        )

        # Check for existing cached summary
        logger.info(f"Checking for existing summary with model {model_name}")
        existing_summary = check_existing_summary(request.document_id, model_name)
        
        if existing_summary:
            logger.info(f"Found existing summary with {existing_summary['word_count']} words, returning from cache")
            
            response = SummarizationResponse(
                success=True,
                document_id=request.document_id,
                document_name=document_name,
                summary_text=existing_summary['summary_text'],
                key_points=existing_summary['key_points'],
                word_count=existing_summary['word_count'],
                model_used=model_name,
                summary_type=config["name"],
                document_type=document_type,
                created_at=existing_summary['created_at'].isoformat() if existing_summary['created_at'] else datetime.utcnow().isoformat(),
                from_cache=True
            )
            return response

        # No cached summary found, proceed with generation
        logger.info(f"No cached summary found, generating new summary using model: {model_name}")

        # Prepare config for the AI service
        ai_config = {
            "model": model_name,
            "name": config["name"]
        }

        # Call the AI service to generate the actual summary
        summary_text = summarize_with_options(document_content, ai_config)
        
        # Calculate actual word count of the generated summary
        word_count = calculate_word_count(summary_text)

        # Store the generated summary in the database for future reference
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
                    conn.commit()
                    logger.info(f"Summary stored in database with word count: {word_count}")
        except Exception as db_error:
            logger.error(f"Failed to store summary in database: {str(db_error)}")

        # Build the response object with all the required information
        response = SummarizationResponse(
            success=True,
            document_id=request.document_id,
            document_name=document_name,
            summary_text=summary_text,
            key_points=None,
            word_count=word_count,
            model_used=model_name,
            summary_type=config["name"],
            document_type=document_type,
            created_at=datetime.utcnow().isoformat(),
            from_cache=False
        )

        logger.info(f"Summary generated successfully using {model_name} with {word_count} words")
        return response

    except HTTPException as e:
        # Re-raise HTTP exceptions (these are expected errors with proper status codes)
        raise
    except Exception as e:
        # Catch any unexpected errors and convert them to HTTP 500 errors
        logger.error(f"Error generating summary: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate summary: {str(e)}"
        )

@router.get("/options")
async def get_available_summary_options():
    """
    Endpoint to get available summarization options and domain-specific models.
    
    Returns:
        dict: Success status and available options with their configurations
    """
    try:
        # Get the current summary type mapping
        mapping = get_summary_mapping()
        domain_mapping = get_domain_specific_model_mapping()
        
        # Return success response with options
        return {
            "success": True,
            "options": mapping,
            "domain_specific_models": domain_mapping
        }
    except Exception as e:
        logger.error(f"Error getting summary options: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get summary options"
        )

@router.get("/document-types")
async def get_available_document_types():
    """
    Endpoint to get all available document types for domain-specific summaries.
    
    Returns:
        dict: Success status and list of supported document types
    """
    try:
        domain_mapping = get_domain_specific_model_mapping()
        
        return {
            "success": True,
            "document_types": list(domain_mapping.keys()),
            "models_mapping": domain_mapping
        }
    except Exception as e:
        logger.error(f"Error getting document types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get document types"
        )


@router.get("/document/{document_id}")
async def get_document_summaries(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all summaries for a specific document"""
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT ds.id, ds.summary_text, ds.model_version, ds.word_count, 
                           ds.created_at, 'cached' as summary_type
                    FROM document_summaries ds
                    JOIN documents d ON ds.document_id = d.id
                    WHERE d.id = %s AND d.user_id = %s
                    ORDER BY ds.created_at DESC
                """
                cursor.execute(query, (document_id, str(current_user.id)))
                results = cursor.fetchall()
                
                summaries = []
                for result in results:
                    summaries.append({
                        "id": result[0],
                        "summary_text": result[1],
                        "model_used": result[2],
                        "word_count": result[3],
                        "created_at": result[4],
                        "summary_type": "Brief Summary",  # You might want to store this
                        "from_cache": True
                    })
                
                return {"success": True, "summaries": summaries}
                
    except Exception as e:
        logger.error(f"Error fetching document summaries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch summaries")



@router.get("/user/recent")
async def get_user_recent_summaries(
    limit: int = 5,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get recent summaries for the current user across all documents.
    
    Args:
        limit: Maximum number of summaries to return (default: 5)
        current_user: Authenticated user (injected by dependency)
    
    Returns:
        dict: Success status and list of recent summaries with document details
    """
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Query to get recent summaries with document details
                query = """
                    SELECT 
                        ds.id,
                        ds.summary_text,
                        ds.model_version,
                        ds.word_count,
                        ds.created_at,
                        d.id as document_id,
                        d.original_filename as document_name,
                        d.created_at as document_created_at
                    FROM document_summaries ds
                    JOIN documents d ON ds.document_id = d.id
                    WHERE d.user_id = %s
                    ORDER BY ds.created_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (str(current_user.id), limit))
                results = cursor.fetchall()
                
                summaries = []
                for result in results:
                    summaries.append({
                        "id": result[0],
                        "summary_text": result[1],
                        "model_used": result[2],
                        "word_count": result[3],
                        "created_at": result[4].isoformat() if result[4] else None,
                        "document_id": result[5],
                        "document_name": result[6],
                        "document_created_at": result[7].isoformat() if result[7] else None,
                        "summary_type": "Summary",
                        "from_cache": True
                    })
                
                return {
                    "success": True,
                    "summaries": summaries,
                    "count": len(summaries)
                }
                
    except Exception as e:
        logger.error(f"Error fetching user recent summaries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent summaries")
