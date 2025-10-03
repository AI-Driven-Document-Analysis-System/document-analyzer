from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from pydantic import BaseModel
from app.services.document_selection_service import document_selection_service
from ..core.dependencies import get_current_user
from ..schemas.user_schemas import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-selections", tags=["document-selections"])

class DocumentSelectionRequest(BaseModel):
    document_ids: List[str]  # Changed from int to str (UUIDs)

class DocumentSelectionResponse(BaseModel):
    user_id: str
    document_ids: List[str]  # Changed from int to str (UUIDs)
    created_at: str
    updated_at: str

@router.post("/save", response_model=DocumentSelectionResponse)
async def save_document_selection(
    request: DocumentSelectionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Save user's document selection for Knowledge Base mode"""
    try:
        user_id = current_user.id
        
        selection = await document_selection_service.save_user_document_selection(
            user_id=user_id,
            document_ids=request.document_ids
        )
        
        return DocumentSelectionResponse(
            user_id=str(selection.user_id),
            document_ids=selection.selected_document_ids,
            created_at=selection.created_at.isoformat(),
            updated_at=selection.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error saving document selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save document selection")

@router.get("/", response_model=DocumentSelectionResponse)
async def get_document_selection(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's document selection"""
    try:
        user_id = current_user.id
        
        selection = await document_selection_service.get_user_document_selection(user_id)
        
        if not selection:
            # Return empty selection if none exists
            return DocumentSelectionResponse(
                user_id=str(user_id),
                document_ids=[],
                created_at="",
                updated_at=""
            )
        
        return DocumentSelectionResponse(
            user_id=str(selection.user_id),
            document_ids=selection.selected_document_ids,
            created_at=selection.created_at.isoformat(),
            updated_at=selection.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting document selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document selection")

@router.delete("/clear")
async def clear_document_selection(
    current_user: UserResponse = Depends(get_current_user)
):
    """Clear user's document selection"""
    try:
        user_id = current_user.id
        
        await document_selection_service.clear_user_document_selection(user_id)
        
        return {"message": "Document selection cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing document selection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear document selection")
