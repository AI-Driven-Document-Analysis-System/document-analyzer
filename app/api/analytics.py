from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..api.auth import get_current_user
from ..schemas.user_schemas import UserResponse
from ..core.database import db_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/document-uploads-over-time")
async def get_document_uploads_over_time(
    period: str = "30d",  # 7d, 30d, 90d, 1y
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document upload statistics over time for the current user."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        user_id = str(current_user.id)
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
            group_by = "DATE(upload_timestamp)"
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
            group_by = "DATE(upload_timestamp)"
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
            group_by = "DATE_TRUNC('week', upload_timestamp)"
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
            group_by = "DATE_TRUNC('month', upload_timestamp)"
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use: 7d, 30d, 90d, or 1y")
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get document uploads over time
                query = f"""
                    SELECT 
                        {group_by} as date,
                        COUNT(*) as upload_count,
                        SUM(file_size) as total_size
                    FROM documents 
                    WHERE user_id = %s 
                        AND upload_timestamp >= %s 
                        AND upload_timestamp <= %s
                    GROUP BY {group_by}
                    ORDER BY date
                """
                
                cursor.execute(query, (user_id, start_date, end_date))
                results = cursor.fetchall()
                
                # Format data for frontend
                chart_data = []
                for row in results:
                    chart_data.append({
                        "date": row[0].isoformat() if row[0] else None,
                        "uploads": row[1] or 0,
                        "totalSize": row[2] or 0
                    })
                
                # Get summary statistics
                summary_query = """
                    SELECT 
                        COUNT(*) as total_documents,
                        SUM(file_size) as total_size,
                        AVG(file_size) as avg_size,
                        MIN(upload_timestamp) as first_upload,
                        MAX(upload_timestamp) as last_upload
                    FROM documents 
                    WHERE user_id = %s
                """
                
                cursor.execute(summary_query, (user_id,))
                summary = cursor.fetchone()
                
                return {
                    "chartData": chart_data,
                    "summary": {
                        "totalDocuments": summary[0] or 0,
                        "totalSize": summary[1] or 0,
                        "averageSize": round(summary[2] or 0, 2),
                        "firstUpload": summary[3].isoformat() if summary[3] else None,
                        "lastUpload": summary[4].isoformat() if summary[4] else None
                    },
                    "period": period
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document upload analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@router.get("/document-types-distribution")
async def get_document_types_distribution(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document types distribution for the current user."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        dc.document_type,
                        COUNT(*) as count,
                        AVG(d.file_size) as avg_size
                    FROM documents d
                    LEFT JOIN document_classifications dc ON d.id = dc.document_id
                    WHERE d.user_id = %s
                    GROUP BY dc.document_type
                    ORDER BY count DESC
                """
                
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                
                chart_data = []
                for row in results:
                    chart_data.append({
                        "type": row[0] or "Unknown",
                        "count": row[1] or 0,
                        "avgSize": round(row[2] or 0, 2)
                    })
                
                return {
                    "chartData": chart_data
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document types distribution: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document types: {str(e)}")

@router.get("/upload-trends")
async def get_upload_trends(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get upload trends and patterns for the current user."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        user_id = str(current_user.id)
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get uploads by day of week
                day_of_week_query = """
                    SELECT 
                        EXTRACT(DOW FROM upload_timestamp) as day_of_week,
                        COUNT(*) as count
                    FROM documents 
                    WHERE user_id = %s
                    GROUP BY EXTRACT(DOW FROM upload_timestamp)
                    ORDER BY day_of_week
                """
                
                cursor.execute(day_of_week_query, (user_id,))
                day_results = cursor.fetchall()
                
                # Get uploads by hour of day
                hour_query = """
                    SELECT 
                        EXTRACT(HOUR FROM upload_timestamp) as hour,
                        COUNT(*) as count
                    FROM documents 
                    WHERE user_id = %s
                    GROUP BY EXTRACT(HOUR FROM upload_timestamp)
                    ORDER BY hour
                """
                
                cursor.execute(hour_query, (user_id,))
                hour_results = cursor.fetchall()
                
                # Format data
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                day_data = []
                for row in day_results:
                    day_data.append({
                        "day": days[int(row[0])],
                        "count": row[1] or 0
                    })
                
                hour_data = []
                for row in hour_results:
                    hour_data.append({
                        "hour": f"{int(row[0]):02d}:00",
                        "count": row[1] or 0
                    })
                
                return {
                    "byDayOfWeek": day_data,
                    "byHourOfDay": hour_data
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upload trends: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving trends: {str(e)}")

@router.get("/storage-usage")
async def get_storage_usage(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get storage usage statistics for the current user."""
    try:
        if not hasattr(current_user, 'id') or current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        user_id = str(current_user.id)
        TOTAL_STORAGE = 300*1024*1024   # 2GB in bytes
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT SUM(file_size) as total_used
                    FROM documents 
                    WHERE user_id = %s
                """
                
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                used_storage = result[0] or 0
                
                return {
                    "totalStorage": TOTAL_STORAGE,
                    "usedStorage": used_storage,
                    "availableStorage": TOTAL_STORAGE - used_storage,
                    "usagePercentage": (used_storage / TOTAL_STORAGE) * 100
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storage usage: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving storage usage: {str(e)}")
