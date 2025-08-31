from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from ..core.database import db_manager
from ..schemas.user_schemas import UserResponse, ChangeEmailRequest, ChangePasswordRequest
from ..core.dependencies import get_current_user
from ..db.crud import get_user_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

@router.post("/change-email")
async def change_email(
    request: ChangeEmailRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Change user email address"""
    try:
        user_crud = get_user_crud()
        if not user_crud:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Change email
        updated_user = user_crud.change_user_email(
            user_id=current_user.id,
            new_email=request.new_email,
            password=request.password
        )
        
        if not updated_user:
            raise HTTPException(status_code=400, detail="Invalid password or email already exists")
        
        logger.info(f"User {current_user.id} changed email to {request.new_email}")
        return {"message": "Email changed successfully", "new_email": request.new_email}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Change user password"""
    try:
        user_crud = get_user_crud()
        if not user_crud:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Change password
        updated_user = user_crud.change_user_password(
            user_id=current_user.id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        if not updated_user:
            raise HTTPException(status_code=400, detail="Invalid current password")
        
        logger.info(f"User {current_user.id} changed password successfully")
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me")
async def get_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get comprehensive user profile with statistics and activity data."""
    try:
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get user basic info
                cursor.execute("""
                    SELECT id, email, first_name, last_name, created_at
                    FROM users 
                    WHERE id = %s
                """, (user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    raise HTTPException(status_code=404, detail="User not found")
                
                # Get document count
                cursor.execute("""
                    SELECT COUNT(*) as document_count
                    FROM documents 
                    WHERE user_id = %s
                """, (user_id,))
                
                doc_count_result = cursor.fetchone()
                documents_count = doc_count_result[0] if doc_count_result else 0
                
                # Get upload activity for the last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                cursor.execute("""
                    SELECT 
                        DATE(upload_timestamp) as upload_date,
                        COUNT(*) as count
                    FROM documents 
                    WHERE user_id = %s 
                        AND upload_timestamp >= %s
                    GROUP BY DATE(upload_timestamp)
                    ORDER BY upload_date ASC
                """, (user_id, thirty_days_ago))
                
                activity_data = cursor.fetchall()
                
                # Create a complete 30-day activity chart (fill missing days with 0)
                upload_activity = []
                current_date = thirty_days_ago.date()
                end_date = datetime.now().date()
                
                # Convert activity data to dict for easy lookup
                activity_dict = {row[0]: row[1] for row in activity_data}
                
                while current_date <= end_date:
                    upload_activity.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "count": activity_dict.get(current_date, 0)
                    })
                    current_date += timedelta(days=1)
                
                # Determine user plan (you can customize this logic)
                plan_info = determine_user_plan(documents_count)
                
                profile_data = {
                    "id": str(user_data[0]),
                    "email": user_data[1],
                    "first_name": user_data[2],
                    "last_name": user_data[3],
                    "created_at": user_data[4].isoformat() if user_data[4] else None,
                    "documents_count": documents_count,
                    "current_plan": plan_info["name"],
                    "plan_features": plan_info["features"],
                    "upload_activity": upload_activity
                }
                
                return profile_data
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def determine_user_plan(documents_count: int) -> Dict[str, Any]:
    """Determine user plan based on usage. You can customize this logic."""
    if documents_count >= 100:
        return {
            "name": "Enterprise",
            "features": {
                "documents_per_month": "Unlimited",
                "storage_gb": "100",
                "api_calls_per_day": "10000",
                "priority_support": "Yes"
            }
        }
    elif documents_count >= 25:
        return {
            "name": "Pro",
            "features": {
                "documents_per_month": "100",
                "storage_gb": "10",
                "api_calls_per_day": "1000",
                "priority_support": "No"
            }
        }
    else:
        return {
            "name": "Free",
            "features": {
                "documents_per_month": "10",
                "storage_gb": "1",
                "api_calls_per_day": "100",
                "priority_support": "No"
            }
        }

@router.get("/stats")
async def get_user_stats(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get detailed user statistics."""
    try:
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get comprehensive stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_documents,
                        COUNT(CASE WHEN upload_timestamp >= NOW() - INTERVAL '7 days' THEN 1 END) as documents_this_week,
                        COUNT(CASE WHEN upload_timestamp >= NOW() - INTERVAL '30 days' THEN 1 END) as documents_this_month,
                        COALESCE(SUM(file_size), 0) as total_storage_used,
                        COUNT(CASE WHEN mime_type LIKE 'application/pdf%' THEN 1 END) as pdf_count,
                        COUNT(CASE WHEN mime_type LIKE 'image/%' THEN 1 END) as image_count,
                        COUNT(CASE WHEN mime_type LIKE 'text/%' THEN 1 END) as text_count
                    FROM documents 
                    WHERE user_id = %s
                """, (user_id,))
                
                stats = cursor.fetchone()
                
                if not stats:
                    stats = (0, 0, 0, 0, 0, 0, 0)
                
                return {
                    "total_documents": stats[0],
                    "documents_this_week": stats[1],
                    "documents_this_month": stats[2],
                    "total_storage_used_bytes": stats[3],
                    "total_storage_used_mb": round(stats[3] / (1024 * 1024), 2) if stats[3] else 0,
                    "document_types": {
                        "pdf": stats[4],
                        "images": stats[5],
                        "text": stats[6],
                        "other": stats[0] - stats[4] - stats[5] - stats[6]
                    }
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")