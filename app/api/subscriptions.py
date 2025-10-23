from fastapi import APIRouter, Depends, HTTPException
from ..core.dependencies import get_current_user
from ..core.database import db_manager
from ..schemas.user_schemas import UserResponse
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

class CreateSubscriptionRequest(BaseModel):
    name: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: Optional[bool] = True

class SubscriptionResponse(BaseModel):
    user_id: str
    plan_id: Optional[str]
    name: str
    status: str
    started_at: Optional[datetime]
    expires_at: Optional[datetime]
    auto_renew: Optional[bool]


@router.get('/me', response_model=Optional[SubscriptionResponse])
async def get_my_subscription(current_user: UserResponse = Depends(get_current_user)):
    """Return the active subscription for the current user, or null if free tier."""
    try:
        user_id = current_user.id
        query = "SELECT us.user_id, us.plan_id, sp.name, us.status, us.started_at, us.expires_at, us.auto_renew FROM user_subscriptions as us LEFT JOIN subscription_plans as sp ON us.plan_id = sp.id WHERE user_id = %s ORDER BY started_at DESC LIMIT 1"
        with db_manager.get_cursor(commit=False) as cursor:
            cursor.execute(query, (str(user_id),))
            row = cursor.fetchone()
            if not row:
                return None
            # Ensure UUID fields are converted to strings for Pydantic
            result = {
                'user_id': str(row.get('user_id')) if row.get('user_id') is not None else None,
                'plan_id': str(row.get('plan_id')) if row.get('plan_id') is not None else None,
                'name': row.get('name'),
                'status': row.get('status'),
                'started_at': row.get('started_at'),
                'expires_at': row.get('expires_at'),
                'auto_renew': row.get('auto_renew')
            }
            return SubscriptionResponse(**result)
    except Exception as e:
        logger.exception("Failed to fetch subscription")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post('/', response_model=SubscriptionResponse)
async def create_subscription(payload: CreateSubscriptionRequest, current_user: UserResponse = Depends(get_current_user)):
    """Create a user subscription entry after successful payment/webhook.
    This endpoint should be called by the backend after payment completes (or by the frontend after verifying session status).
    """
    try:
        user_id = current_user.id
        now = payload.started_at or datetime.utcnow()
        expires = payload.expires_at
        if not expires:
            # Default to 1 month for demonstration
            expires = now + timedelta(days=30)
        
        # Look up plan id by name
        select_sql = "SELECT id FROM subscription_plans WHERE name = %s"
        with db_manager.get_cursor(commit=False) as cursor:
            cursor.execute(select_sql, (payload.name,))
            plan_row = cursor.fetchone()
            if not plan_row:
                raise HTTPException(status_code=400, detail="Invalid subscription plan name")
            plan_id = plan_row['id']
        insert_sql = "INSERT INTO user_subscriptions (user_id, plan_id, status, started_at, expires_at, auto_renew) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, user_id, plan_id, status, started_at, expires_at, auto_renew"
        with db_manager.get_cursor(commit=True) as cursor:
            cursor.execute(insert_sql, (str(user_id), plan_id, 'active', now, expires, payload.auto_renew))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=500, detail='Failed to insert subscription')
            response = {
                'user_id': str(row.get('user_id')) if row.get('user_id') is not None else None,
                'plan_id': str(row.get('plan_id')) if row.get('plan_id') is not None else None,
                'name': payload.name,
                'status': row.get('status'),
                'started_at': row.get('started_at'),
                'expires_at': row.get('expires_at'),
                'auto_renew': row.get('auto_renew')
            }
            return SubscriptionResponse(**response)
    except Exception as e:
        logger.exception("Failed to create subscription")
        raise HTTPException(status_code=500, detail="Internal error")

@router.post('/change', response_model=SubscriptionResponse)
async def change_subscription(payload: CreateSubscriptionRequest, current_user: UserResponse = Depends(get_current_user)):
    """Change the current user's active subscription."""
    try:
        user_id = current_user.id
        now = payload.started_at or datetime.utcnow()
        if not payload.expires_at:
            # Default to 1 month for demonstration
            expires = now + timedelta(days=365)
        
        # Look up plan id by name
        select_sql = "SELECT id FROM subscription_plans WHERE name = %s"
        with db_manager.get_cursor(commit=False) as cursor:
            cursor.execute(select_sql, (payload.name,))
            plan_row = cursor.fetchone()
            if not plan_row:
                raise HTTPException(status_code=400, detail="Invalid subscription plan name")
            plan_id = plan_row['id']
        update_sql = "UPDATE user_subscriptions SET plan_id = %s, status = %s, started_at = %s, expires_at = %s, auto_renew = %s WHERE user_id = %s RETURNING id, user_id, plan_id, status, started_at, expires_at, auto_renew"
        with db_manager.get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, (plan_id, 'active', now, expires, payload.auto_renew, str(user_id)))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=500, detail='Failed to update subscription')
            response = {
                'user_id': str(row.get('user_id')) if row.get('user_id') is not None else None,
                'plan_id': str(row.get('plan_id')) if row.get('plan_id') is not None else None,
                'name': payload.name,
                'status': row.get('status'),
                'started_at': row.get('started_at'),
                'expires_at': row.get('expires_at'),
                'auto_renew': row.get('auto_renew')
            }
            return SubscriptionResponse(**response)
    except Exception as e:
        logger.exception("Failed to update subscription")
        raise HTTPException(status_code=500, detail="Internal error")