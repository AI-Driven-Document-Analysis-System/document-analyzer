from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
import hashlib

from .security import verify_token
from .user_cache import user_cache
from ..db.crud import get_user_crud
from ..schemas.user_schemas import UserResponse

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user with caching optimization"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Try cache first to avoid database hit
        cached_user = user_cache.get(user_id)
        if cached_user:
            return cached_user
        
        # Cache miss - get from database
        user_crud = get_user_crud()
        user = user_crud.get_user_by_id(UUID(user_id))
        
        if user is None:
            raise credentials_exception
        
        # Create response and cache it
        user_response = UserResponse(**user.__dict__)
        user_cache.set(user_id, user_response)
        
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Authentication error: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user"""
    return current_user
