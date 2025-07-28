# from fastapi import APIRouter, HTTPException, Depends, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from typing import Optional
# from datetime import timedelta
# import logging

# from ..schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate
# from ..db.crud import get_user_crud
# from ..core.security import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
# from ..core.dependencies import get_current_user

# router = APIRouter(prefix="/auth", tags=["authentication"])
# security = HTTPBearer()
# logger = logging.getLogger(__name__)

# @router.post("/register", response_model=UserResponse)
# async def register(user_data: UserCreate):
#     """Register a new user"""
#     try:
#         user_crud = get_user_crud()
        
#         # Check if user already exists
#         existing_user = user_crud.get_user_by_email(user_data.email)
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )
        
#         # Create new user
#         user = user_crud.create_user(
#             email=user_data.email,
#             password=user_data.password,
#             first_name=user_data.first_name,
#             last_name=user_data.last_name
#         )
        
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to create user"
#             )
        
#         logger.info(f"New user registered: {user.email}")
#         return UserResponse(**user.__dict__)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Registration error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )

# @router.post("/login", response_model=Token)
# async def login(user_credentials: UserLogin):
#     """Authenticate user and return access token"""
#     try:
#         user_crud = get_user_crud()
        
#         # Authenticate user
#         user = user_crud.authenticate_user(
#             email=user_credentials.email,
#             password=user_credentials.password
#         )
        
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect email or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
        
#         # Create access token
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": str(user.id), "email": user.email},
#             expires_delta=access_token_expires
#         )
        
#         logger.info(f"User logged in: {user.email}")
        
#         return Token(
#             access_token=access_token,
#             token_type="bearer",
#             user=UserResponse(**user.__dict__)
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Login error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )

# @router.get("/me", response_model=UserResponse)
# async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
#     """Get current user information"""
#     return current_user

# @router.put("/me", response_model=UserResponse)
# async def update_current_user(
#     user_update: UserUpdate,
#     current_user: UserResponse = Depends(get_current_user)
# ):
#     """Update current user information"""
#     try:
#         user_crud = get_user_crud()
        
#         updated_user = user_crud.update_user(
#             user_id=current_user.id,
#             **user_update.dict(exclude_unset=True)
#         )
        
#         if not updated_user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
        
#         return UserResponse(**updated_user.__dict__)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"User update error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )

# @router.post("/logout")
# async def logout():
#     """Logout user (client should remove token)"""
#     return {"message": "Successfully logged out"}




from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import timedelta
import logging
import traceback  # Add this import

from ..schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from ..db.crud import get_user_crud
from ..core.security import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        # Add debug logging
        logger.debug("Getting user CRUD instance")
        user_crud = get_user_crud()
        logger.debug("User CRUD instance obtained successfully")
        
        # Check if user already exists
        logger.debug(f"Checking if user exists: {user_data.email}")
        existing_user = user_crud.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logger.debug("User does not exist, proceeding with creation")
        
        # Create new user
        logger.debug("Creating new user")
        user = user_crud.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        logger.debug("User creation completed")
        
        if not user:
            logger.error("User creation returned None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        logger.info(f"New user registered successfully: {user.email}")
        return UserResponse(**user.__dict__)
        
    except HTTPException:
        logger.error(f"HTTP Exception during registration: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"  # Include error details for debugging
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    try:
        user_crud = get_user_crud()
        
        # Authenticate user
        user = user_crud.authenticate_user(
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.__dict__)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update current user information"""
    try:
        user_crud = get_user_crud()
        
        updated_user = user_crud.update_user(
            user_id=current_user.id,
            **user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**updated_user.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout():
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}