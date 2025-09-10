from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Assuming you have these imports in your main app
from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..schemas.user_schemas import UserResponse

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get overview analytics for the dashboard"""
    try:
        # Total documents
        total_docs_query = text("""
            SELECT COUNT(*) as total_documents
            FROM documents 
            WHERE user_id = :user_id
        """)
        total_docs = db.execute(total_docs_query, {"user_id": user_id}).fetchone()
        
        # Documents this month
        docs_this_month_query = text("""
            SELECT COUNT(*) as documents_this_month
            FROM documents 
            WHERE user_id = :user_id 
            AND upload_timestamp >= date_trunc('month', CURRENT_DATE)
        """)
        docs_this_month = db.execute(docs_this_month_query, {"user_id": user_id}).fetchone()
        
        # Processing status counts
        processing_status_query = text("""
            SELECT dp.processing_status, COUNT(*) as count
            FROM document_processing dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.user_id = :user_id
            GROUP BY dp.processing_status
        """)
        processing_status = db.execute(processing_status_query, {"user_id": user_id}).fetchall()
        
        # Storage usage
        storage_query = text("""
            SELECT SUM(file_size) as total_storage
            FROM documents 
            WHERE user_id = :user_id
        """)
        storage = db.execute(storage_query, {"user_id": user_id}).fetchone()
        
        return {
            "total_documents": total_docs.total_documents or 0,
            "documents_this_month": docs_this_month.documents_this_month or 0,
            "storage_used_bytes": storage.total_storage or 0,
            "processing_status": [
                {"status": row.processing_status, "count": row.count} 
                for row in processing_status
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching overview: {str(e)}")

@router.get("/document-types")
async def get_document_types_analytics(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document types distribution"""
    try:
        query = text("""
            SELECT 
                dc.document_type,
                COUNT(*) as count,
                ROUND(AVG(dc.confidence_score), 2) as avg_confidence
            FROM document_classifications dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.user_id = :user_id
            GROUP BY dc.document_type
            ORDER BY count DESC
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "document_type": row.document_type,
                "count": row.count,
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence else 0
            }
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document types: {str(e)}")

@router.get("/upload-trends")
async def get_upload_trends(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document upload trends over time"""
    try:
        query = text("""
            SELECT 
                DATE(upload_timestamp) as upload_date,
                COUNT(*) as document_count,
                SUM(file_size) as total_size
            FROM documents
            WHERE user_id = :user_id
            AND upload_timestamp >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(upload_timestamp)
            ORDER BY upload_date
        """ % days)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "date": row.upload_date.isoformat() if row.upload_date else None,
                "document_count": row.document_count,
                "total_size": row.total_size or 0
            }
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upload trends: {str(e)}")

@router.get("/processing-performance")
async def get_processing_performance(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get processing performance metrics"""
    try:
        query = text("""
            SELECT 
                d.mime_type,
                COUNT(*) as total_processed,
                AVG(CASE WHEN dp.ocr_completed_at IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (dp.ocr_completed_at - d.upload_timestamp))/60 
                    ELSE NULL END) as avg_ocr_time_minutes,
                AVG(CASE WHEN dp.classification_completed_at IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (dp.classification_completed_at - d.upload_timestamp))/60 
                    ELSE NULL END) as avg_classification_time_minutes,
                COUNT(CASE WHEN dp.processing_status = 'completed' THEN 1 END) as successful_processing,
                COUNT(CASE WHEN dp.processing_status = 'failed' THEN 1 END) as failed_processing
            FROM documents d
            JOIN document_processing dp ON d.id = dp.document_id
            WHERE d.user_id = :user_id
            GROUP BY d.mime_type
            ORDER BY total_processed DESC
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "mime_type": row.mime_type,
                "total_processed": row.total_processed,
                "avg_ocr_time_minutes": round(float(row.avg_ocr_time_minutes), 2) if row.avg_ocr_time_minutes else None,
                "avg_classification_time_minutes": round(float(row.avg_classification_time_minutes), 2) if row.avg_classification_time_minutes else None,
                "success_rate": round((row.successful_processing / row.total_processed) * 100, 2) if row.total_processed > 0 else 0,
                "failed_count": row.failed_processing
            }
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching processing performance: {str(e)}")

@router.get("/content-insights")
async def get_content_insights(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get content-related insights"""
    try:
        query = text("""
            SELECT 
                COUNT(CASE WHEN dc.has_tables = true THEN 1 END) as documents_with_tables,
                COUNT(CASE WHEN dc.has_images = true THEN 1 END) as documents_with_images,
                AVG(dc.ocr_confidence_score) as avg_ocr_confidence,
                COUNT(CASE WHEN d.language_detected IS NOT NULL THEN 1 END) as documents_with_language_detection,
                d.language_detected,
                COUNT(*) as count_per_language
            FROM document_content dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.user_id = :user_id
            GROUP BY d.language_detected
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        # Get overall stats
        overall_query = text("""
            SELECT 
                COUNT(CASE WHEN dc.has_tables = true THEN 1 END) as total_with_tables,
                COUNT(CASE WHEN dc.has_images = true THEN 1 END) as total_with_images,
                AVG(dc.ocr_confidence_score) as overall_avg_ocr_confidence,
                COUNT(*) as total_documents
            FROM document_content dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.user_id = :user_id
        """)
        
        overall = db.execute(overall_query, {"user_id": user_id}).fetchone()
        
        return {
            "overall": {
                "documents_with_tables": overall.total_with_tables or 0,
                "documents_with_images": overall.total_with_images or 0,
                "avg_ocr_confidence": round(float(overall.overall_avg_ocr_confidence), 4) if overall.overall_avg_ocr_confidence else 0,
                "total_documents": overall.total_documents or 0
            },
            "language_distribution": [
                {
                    "language": row.language_detected or "unknown",
                    "count": row.count_per_language
                }
                for row in result
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching content insights: {str(e)}")

@router.get("/usage-limits")
async def get_usage_limits(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current usage limits and subscription info"""
    try:
        usage_query = text("""
            SELECT 
                documents_processed_monthly,
                handwriting_recognition_used,
                risk_assessments_used,
                citation_analysis_used,
                reset_date
            FROM user_usage_limits
            WHERE user_id = :user_id
        """)
        
        subscription_query = text("""
            SELECT 
                sp.name as plan_name,
                sp.features,
                us.status,
                us.expires_at
            FROM user_subscriptions us
            JOIN subscription_plans sp ON us.plan_id = sp.id
            WHERE us.user_id = :user_id
            AND us.status = 'active'
            ORDER BY us.created_at DESC
            LIMIT 1
        """)
        
        usage = db.execute(usage_query, {"user_id": user_id}).fetchone()
        subscription = db.execute(subscription_query, {"user_id": user_id}).fetchone()
        
        return {
            "usage": {
                "documents_processed_monthly": usage.documents_processed_monthly if usage else 0,
                "handwriting_recognition_used": usage.handwriting_recognition_used if usage else 0,
                "risk_assessments_used": usage.risk_assessments_used if usage else 0,
                "citation_analysis_used": usage.citation_analysis_used if usage else 0,
                "reset_date": usage.reset_date.isoformat() if usage and usage.reset_date else None
            },
            "subscription": {
                "plan_name": subscription.plan_name if subscription else "Free",
                "features": json.loads(subscription.features) if subscription and subscription.features else {},
                "status": subscription.status if subscription else "free",
                "expires_at": subscription.expires_at.isoformat() if subscription and subscription.expires_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage limits: {str(e)}")

@router.get("/tag-analytics")
async def get_tag_analytics(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get tag usage analytics"""
    try:
        query = text("""
            SELECT 
                dt.tag,
                dt.tag_type,
                COUNT(*) as usage_count
            FROM document_tags dt
            JOIN documents d ON dt.document_id = d.id
            WHERE d.user_id = :user_id
            GROUP BY dt.tag, dt.tag_type
            ORDER BY usage_count DESC
            LIMIT 20
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "tag": row.tag,
                "tag_type": row.tag_type,
                "usage_count": row.usage_count
            }
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tag analytics: {str(e)}")

@router.get("/productivity-insights")
async def get_productivity_insights(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get creative productivity insights"""
    try:
        # Peak upload hours
        peak_hours_query = text("""
            SELECT 
                EXTRACT(HOUR FROM upload_timestamp) as hour,
                COUNT(*) as upload_count,
                AVG(file_size) as avg_file_size
            FROM documents
            WHERE user_id = :user_id
            AND upload_timestamp >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY EXTRACT(HOUR FROM upload_timestamp)
            ORDER BY upload_count DESC
        """)
        
        # Document velocity (docs per day trend)
        velocity_query = text("""
            SELECT 
                DATE(upload_timestamp) as date,
                COUNT(*) as daily_count,
                LAG(COUNT(*)) OVER (ORDER BY DATE(upload_timestamp)) as prev_day_count
            FROM documents
            WHERE user_id = :user_id
            AND upload_timestamp >= CURRENT_DATE - INTERVAL '14 days'
            GROUP BY DATE(upload_timestamp)
            ORDER BY date
        """)
        
        # Processing efficiency score
        efficiency_query = text("""
            SELECT 
                AVG(CASE 
                    WHEN dp.processing_status = 'completed' AND dc.ocr_confidence_score > 0.8 THEN 100
                    WHEN dp.processing_status = 'completed' AND dc.ocr_confidence_score > 0.6 THEN 80
                    WHEN dp.processing_status = 'completed' THEN 60
                    WHEN dp.processing_status = 'failed' THEN 0
                    ELSE 40
                END) as efficiency_score,
                COUNT(*) as total_processed
            FROM document_processing dp
            JOIN documents d ON dp.document_id = d.id
            LEFT JOIN document_content dc ON d.id = dc.document_id
            WHERE d.user_id = :user_id
        """)
        
        peak_hours = db.execute(peak_hours_query, {"user_id": user_id}).fetchall()
        velocity = db.execute(velocity_query, {"user_id": user_id}).fetchall()
        efficiency = db.execute(efficiency_query, {"user_id": user_id}).fetchone()
        
        return {
            "peak_hours": [
                {
                    "hour": int(row.hour),
                    "upload_count": row.upload_count,
                    "avg_file_size": float(row.avg_file_size) if row.avg_file_size else 0
                }
                for row in peak_hours
            ],
            "velocity_trend": [
                {
                    "date": row.date.isoformat(),
                    "daily_count": row.daily_count,
                    "growth": ((row.daily_count - row.prev_day_count) / row.prev_day_count * 100) 
                             if row.prev_day_count and row.prev_day_count > 0 else 0
                }
                for row in velocity
            ],
            "efficiency_score": round(float(efficiency.efficiency_score), 2) if efficiency.efficiency_score else 0,
            "total_processed": efficiency.total_processed if efficiency else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching productivity insights: {str(e)}")

@router.get("/document-journey")
async def get_document_journey(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Track the journey from upload to completion"""
    try:
        journey_query = text("""
            SELECT 
                d.id,
                d.original_filename,
                d.upload_timestamp,
                dp.ocr_completed_at,
                dp.classification_completed_at,
                dp.summarization_completed_at,
                dp.indexing_completed_at,
                dc.document_type,
                ds.summary_text IS NOT NULL as has_summary,
                de.embedding_id IS NOT NULL as has_embedding
            FROM documents d
            LEFT JOIN document_processing dp ON d.id = dp.document_id
            LEFT JOIN document_classifications dc ON d.id = dc.document_id
            LEFT JOIN document_summaries ds ON d.id = ds.document_id
            LEFT JOIN document_embeddings de ON d.id = de.document_id
            WHERE d.user_id = :user_id
            ORDER BY d.upload_timestamp DESC
            LIMIT 10
        """)
        
        result = db.execute(journey_query, {"user_id": user_id}).fetchall()
        
        journeys = []
        for row in result:
            steps = []
            if row.upload_timestamp:
                steps.append({"step": "uploaded", "timestamp": row.upload_timestamp.isoformat()})
            if row.ocr_completed_at:
                steps.append({"step": "ocr_completed", "timestamp": row.ocr_completed_at.isoformat()})
            if row.classification_completed_at:
                steps.append({"step": "classified", "timestamp": row.classification_completed_at.isoformat()})
            if row.summarization_completed_at:
                steps.append({"step": "summarized", "timestamp": row.summarization_completed_at.isoformat()})
            if row.indexing_completed_at:
                steps.append({"step": "indexed", "timestamp": row.indexing_completed_at.isoformat()})
            
            journeys.append({
                "document_id": str(row.id),
                "filename": row.original_filename,
                "document_type": row.document_type,
                "completion_percentage": (len([s for s in steps if s["step"] != "uploaded"]) / 4) * 100,
                "steps": steps,
                "has_summary": row.has_summary,
                "has_embedding": row.has_embedding
            })
        
        return journeys
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document journey: {str(e)}")

@router.get("/content-patterns")
async def get_content_patterns(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Analyze content patterns and anomalies"""
    try:
        # File size patterns
        size_pattern_query = text("""
            SELECT 
                CASE 
                    WHEN file_size < 1024*1024 THEN 'Small (< 1MB)'
                    WHEN file_size < 10*1024*1024 THEN 'Medium (1-10MB)'
                    WHEN file_size < 50*1024*1024 THEN 'Large (10-50MB)'
                    ELSE 'Extra Large (> 50MB)'
                END as size_category,
                COUNT(*) as count,
                AVG(dc.ocr_confidence_score) as avg_confidence,
                AVG(d.page_count) as avg_pages
            FROM documents d
            LEFT JOIN document_content dc ON d.id = dc.document_id
            WHERE d.user_id = :user_id
            GROUP BY size_category
        """)
        
        # Upload patterns by day of week
        day_pattern_query = text("""
            SELECT 
                EXTRACT(DOW FROM upload_timestamp) as day_of_week,
                TO_CHAR(upload_timestamp, 'Day') as day_name,
                COUNT(*) as upload_count,
                AVG(file_size) as avg_file_size
            FROM documents
            WHERE user_id = :user_id
            AND upload_timestamp >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY EXTRACT(DOW FROM upload_timestamp), TO_CHAR(upload_timestamp, 'Day')
            ORDER BY day_of_week
        """)
        
        # Content complexity analysis
        complexity_query = text("""
            SELECT 
                d.mime_type,
                AVG(d.page_count) as avg_pages,
                AVG(LENGTH(dc.extracted_text)) as avg_text_length,
                COUNT(CASE WHEN dc.has_tables THEN 1 END) * 100.0 / COUNT(*) as table_percentage,
                COUNT(CASE WHEN dc.has_images THEN 1 END) * 100.0 / COUNT(*) as image_percentage,
                AVG(dc.ocr_confidence_score) as avg_ocr_confidence
            FROM documents d
            LEFT JOIN document_content dc ON d.id = dc.document_id
            WHERE d.user_id = :user_id
            GROUP BY d.mime_type
            HAVING COUNT(*) >= 3
        """)
        
        size_patterns = db.execute(size_pattern_query, {"user_id": user_id}).fetchall()
        day_patterns = db.execute(day_pattern_query, {"user_id": user_id}).fetchall()
        complexity = db.execute(complexity_query, {"user_id": user_id}).fetchall()
        
        return {
            "size_patterns": [
                {
                    "category": row.size_category,
                    "count": row.count,
                    "avg_confidence": round(float(row.avg_confidence), 4) if row.avg_confidence else 0,
                    "avg_pages": round(float(row.avg_pages), 1) if row.avg_pages else 0
                }
                for row in size_patterns
            ],
            "day_patterns": [
                {
                    "day_of_week": int(row.day_of_week),
                    "day_name": row.day_name.strip(),
                    "upload_count": row.upload_count,
                    "avg_file_size": float(row.avg_file_size) if row.avg_file_size else 0
                }
                for row in day_patterns
            ],
            "complexity_analysis": [
                {
                    "mime_type": row.mime_type,
                    "avg_pages": round(float(row.avg_pages), 1) if row.avg_pages else 0,
                    "avg_text_length": int(row.avg_text_length) if row.avg_text_length else 0,
                    "table_percentage": round(float(row.table_percentage), 1),
                    "image_percentage": round(float(row.image_percentage), 1),
                    "avg_ocr_confidence": round(float(row.avg_ocr_confidence), 4) if row.avg_ocr_confidence else 0
                }
                for row in complexity
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching content patterns: {str(e)}")

@router.get("/smart-recommendations")
async def get_smart_recommendations(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Generate smart recommendations based on usage patterns"""
    try:
        # Analyze user behavior for recommendations
        behavior_query = text("""
            SELECT 
                COUNT(*) as total_docs,
                AVG(file_size) as avg_file_size,
                COUNT(CASE WHEN dp.processing_status = 'failed' THEN 1 END) as failed_processing,
                COUNT(CASE WHEN dc.ocr_confidence_score < 0.7 THEN 1 END) as low_confidence_docs,
                COUNT(CASE WHEN d.upload_timestamp >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_uploads,
                COUNT(DISTINCT d.mime_type) as mime_variety,
                COUNT(CASE WHEN ds.summary_text IS NULL THEN 1 END) as unsummarized_docs
            FROM documents d
            LEFT JOIN document_processing dp ON d.id = dp.document_id
            LEFT JOIN document_content dc ON d.id = dc.document_id
            LEFT JOIN document_summaries ds ON d.id = ds.document_id
            WHERE d.user_id = :user_id
        """)
        
        behavior = db.execute(behavior_query, {"user_id": user_id}).fetchone()
        
        recommendations = []
        
        if behavior:
            # Generate contextual recommendations
            if behavior.failed_processing > behavior.total_docs * 0.1:
                recommendations.append({
                    "type": "processing_improvement",
                    "title": "Improve Processing Success Rate",
                    "description": f"You have {behavior.failed_processing} failed processing attempts. Consider optimizing your document formats.",
                    "action": "Review failed documents and consider converting to PDF format",
                    "priority": "high"
                })
            
            if behavior.low_confidence_docs > behavior.total_docs * 0.2:
                recommendations.append({
                    "type": "quality_improvement", 
                    "title": "Enhance OCR Quality",
                    "description": f"{behavior.low_confidence_docs} documents have low OCR confidence. Better scan quality could improve results.",
                    "action": "Use higher resolution scans (300+ DPI) for better text recognition",
                    "priority": "medium"
                })
            
            if behavior.recent_uploads > 10:
                recommendations.append({
                    "type": "organization",
                    "title": "Stay Organized",
                    "description": f"You've uploaded {behavior.recent_uploads} documents recently. Consider using tags for better organization.",
                    "action": "Add tags to recent uploads for easier searching",
                    "priority": "low"
                })
            
            if behavior.unsummarized_docs > 5:
                recommendations.append({
                    "type": "feature_usage",
                    "title": "Leverage Summaries",
                    "description": f"{behavior.unsummarized_docs} documents don't have summaries. Summaries can help you quickly understand content.",
                    "action": "Generate summaries for important documents",
                    "priority": "medium"
                })
            
            if behavior.mime_variety < 3 and behavior.total_docs > 10:
                recommendations.append({
                    "type": "diversification",
                    "title": "Explore Different Formats",
                    "description": "You primarily use a limited set of file formats. Our system supports many more!",
                    "action": "Try uploading different document types to maximize platform benefits",
                    "priority": "low"
                })
        
        return {
            "recommendations": recommendations,
            "user_profile": {
                "total_documents": behavior.total_docs if behavior else 0,
                "avg_file_size": float(behavior.avg_file_size) if behavior and behavior.avg_file_size else 0,
                "processing_success_rate": ((behavior.total_docs - behavior.failed_processing) / behavior.total_docs * 100) if behavior and behavior.total_docs > 0 else 0,
                "format_diversity_score": min(behavior.mime_variety * 20, 100) if behavior else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.get("/collaboration-insights")
async def get_collaboration_insights(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Analyze collaboration patterns and shared content insights"""
    try:
        # Document sharing patterns (if you have sharing functionality)
        sharing_query = text("""
            SELECT 
                d.document_type,
                COUNT(*) as shared_count,
                AVG(file_size) as avg_shared_size
            FROM documents d
            JOIN document_classifications dc ON d.id = dc.document_id
            WHERE d.user_id = :user_id
            -- Add sharing conditions here when implemented
            GROUP BY d.document_type
            ORDER BY shared_count DESC
        """)
        
        # Team productivity metrics (placeholder for future team features)
        team_query = text("""
            SELECT 
                DATE_TRUNC('week', upload_timestamp) as week,
                COUNT(*) as team_uploads,
                SUM(file_size) as team_storage
            FROM documents
            WHERE user_id = :user_id
            AND upload_timestamp >= CURRENT_DATE - INTERVAL '8 weeks'
            GROUP BY DATE_TRUNC('week', upload_timestamp)
            ORDER BY week
        """)
        
        sharing_result = db.execute(sharing_query, {"user_id": user_id}).fetchall()
        team_result = db.execute(team_query, {"user_id": user_id}).fetchall()
        
        return {
            "sharing_patterns": [
                {
                    "document_type": row.document_type,
                    "shared_count": row.shared_count,
                    "avg_shared_size": float(row.avg_shared_size) if row.avg_shared_size else 0
                }
                for row in sharing_result
            ],
            "team_activity": [
                {
                    "week": row.week.isoformat(),
                    "uploads": row.team_uploads,
                    "storage": row.team_storage or 0
                }
                for row in team_result
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching collaboration insights: {str(e)}")
