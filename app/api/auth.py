from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import timedelta
import logging
import traceback

from ..schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from ..db.crud import get_user_crud
from ..core.security import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..core.dependencies import get_current_user
from ..core.user_cache import user_cache

router = APIRouter(prefix="/auth",
                   tags=["authentication"])  # simply what this do is create a new router for the authentication
security = HTTPBearer()  # simply what this do is create a new HTTPBearer security scheme for token authentication
logger = logging.getLogger(__name__)  # simply what this do is create a new logger for the authentication


@router.post("/register", response_model=UserResponse)  # simply what this do is create a new route for the registration
async def register(user_data: UserCreate):  # simply what this do is create a new route for the registration
    """Register a new user"""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")

        # Validate input data
        if not user_data.email or not user_data.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        if not user_data.password or len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )

        # Get user CRUD instance with error handling
        try:  # simply what this do is create a new try catch block for the registration
            user_crud = get_user_crud()  # simply what this do is create a new user_crud instance
            if not user_crud:  # simply what this do is check if the user_crud instance is not None
                logger.error("Failed to get user CRUD instance")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database connection error"
                )
        except Exception as e:
            logger.error(f"Error getting user CRUD: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        # Check if user already exists
        try:
            existing_user = user_crud.get_user_by_email(user_data.email.strip().lower())
            if existing_user:
                logger.info(f"Registration failed - email already exists: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error checking existing user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking user existence"
            )

        # Create new user
        try:
            user = user_crud.create_user(
                email=user_data.email.strip().lower(),
                password=user_data.password,
                first_name=user_data.first_name.strip() if user_data.first_name else None,
                last_name=user_data.last_name.strip() if user_data.last_name else None
            )

            if not user:
                logger.error("User creation returned None")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        logger.info(f"New user registered successfully: {user.email}")
        return UserResponse(**user.__dict__)

    except HTTPException:
        # Don't log HTTPExceptions as errors - they're expected
        raise
    except Exception as e:
        logger.error(f"Unexpected registration error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    try:
        # Validate input
        if not user_credentials.email or not user_credentials.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        if not user_credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )

        # Get user CRUD instance
        try:
            user_crud = get_user_crud()
            if not user_crud:
                logger.error("Failed to get user CRUD instance")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database connection error"
                )
        except Exception as e:
            logger.error(f"Error getting user CRUD: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        # Authenticate user
        try:
            user = user_crud.authenticate_user(
                email=user_credentials.email.strip().lower(),
                password=user_credentials.password
            )

            if not user:
                logger.info(f"Failed login attempt for email: {user_credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )

        # Create access token
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation error"
            )

        logger.info(f"User logged in successfully: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.__dict__)
        )

    except HTTPException:
        # Don't log HTTPExceptions as errors - they're expected
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/current-user-id")
async def get_current_user_id(current_user: UserResponse = Depends(get_current_user)):
    """Get current user ID only - useful for embedding scripts"""
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return {"user_id": current_user.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user ID error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user ID"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
        user_update: UserUpdate,
        current_user: UserResponse = Depends(get_current_user)
):
    """Update current user information"""
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        # Get user CRUD instance
        try:
            user_crud = get_user_crud()
            if not user_crud:
                logger.error("Failed to get user CRUD instance")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database connection error"
                )
        except Exception as e:
            logger.error(f"Error getting user CRUD: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        # Prepare update data
        update_data = user_update.dict(exclude_unset=True)

        # Clean and validate update data
        if 'email' in update_data and update_data['email']:
            update_data['email'] = update_data['email'].strip().lower()
        if 'first_name' in update_data and update_data['first_name']:
            update_data['first_name'] = update_data['first_name'].strip()
        if 'last_name' in update_data and update_data['last_name']:
            update_data['last_name'] = update_data['last_name'].strip()

        # Update user
        try:
            updated_user = user_crud.update_user(
                user_id=current_user.id,
                **update_data
            )

            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Invalidate cache after user update
            user_cache.invalidate(str(current_user.id))

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

        logger.info(f"User updated successfully: {updated_user.email}")
        return UserResponse(**updated_user.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected user update error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/google-oauth", response_model=Token)
async def google_oauth(oauth_data: dict):
    """Handle Google OAuth authentication (supports both Appwrite and Supabase)"""
    try:
        email = oauth_data.get('email')
        first_name = oauth_data.get('firstName', '')
        last_name = oauth_data.get('lastName', '')
        google_id = oauth_data.get('googleId')

        # Support for Supabase tokens (optional)
        supabase_access_token = oauth_data.get('supabaseAccessToken')
        supabase_refresh_token = oauth_data.get('supabaseRefreshToken')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required from Google OAuth"
            )

        # Get user CRUD instance
        user_crud = get_user_crud()
        if not user_crud:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        # Check if user exists
        existing_user = user_crud.get_user_by_email(email.strip().lower())

        if existing_user:
            # User exists, update Google ID if not set
            if not hasattr(existing_user, 'google_id') or not existing_user.google_id:
                user_crud.update_user(existing_user.id, google_id=google_id)
            user = existing_user
        else:
            # Create new user with Google OAuth data
            user = user_crud.create_user(
                email=email.strip().lower(),
                password=None,  # No password for OAuth users
                first_name=first_name.strip() if first_name else None,
                last_name=last_name.strip() if last_name else None,
                google_id=google_id,
                is_oauth_user=True
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        logger.info(f"Google OAuth successful for user: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.__dict__)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth authentication failed"
        )


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    try:
        if current_user:
            logger.info(f"User logged out: {current_user.email}")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        # Don't fail logout even if there's an error
        return {"message": "Logged out"}


# Health check endpoint
@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    try:
        return {"status": "healthy", "service": "auth", "message": "Authentication service is running"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "message": "Service error"}


@router.get("/cache/stats")
async def get_cache_stats():
    """Get user cache statistics - for monitoring"""
    return {
        "cache_stats": user_cache.stats(),
        "status": "healthy"
    }

