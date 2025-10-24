import stripe
import os
from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
from typing import Optional
from typing import Dict

load_dotenv()

stripe_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_key


class PaymentRequest(BaseModel):
    amount: float
    currency: str = 'usd'
    description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

logger = logging.getLogger(__name__)

# Debug: Check if API key is loaded (after logger is defined)
if not stripe_key:
    logger.error("❌ STRIPE_SECRET_KEY environment variable not found!")
    logger.info(f"Available env vars starting with STRIPE: {[k for k in os.environ.keys() if k.startswith('STRIPE')]}")
    logger.info("Please check your .env file or environment variables")
else:
    logger.info(f"✅ Stripe API key loaded: {'sk_test_' if stripe_key.startswith('sk_test_') else 'sk_live_' if stripe_key.startswith('sk_live_') else 'unknown format'}...{stripe_key[-4:]}")



router = APIRouter(prefix="/payments", tags=["payments"])

YOUR_DOMAIN = 'http://localhost:3000'

# @router.post('/create-payment-intent')
# async def create_payment(payment_request: PaymentRequest):
#     try:
#         # The amount should be in the smallest currency unit (e.g., cents)
#         amount_in_cents = int(payment_request.amount * 100)

#         # Create payment intent with additional metadata
#         intent_data = {
#             'amount': amount_in_cents,
#             'currency': payment_request.currency,
#             'automatic_payment_methods': {"enabled": True},
#         }
        
#         # Add optional metadata
#         if payment_request.description:
#             intent_data['description'] = payment_request.description
            
#         # Add customer metadata
#         metadata = {}
#         if payment_request.customer_name:
#             metadata['customer_name'] = payment_request.customer_name
#         if payment_request.customer_email:
#             metadata['customer_email'] = payment_request.customer_email
            
#         if metadata:
#             intent_data['metadata'] = metadata

#         intent = stripe.PaymentIntent.create(**intent_data)
        
#         return {
#             "clientSecret": intent.client_secret,
#             "amount": payment_request.amount,
#             "currency": payment_request.currency
#         }
#     except Exception as e:
#         logger.error(f"Error creating payment intent: {e}")
#         raise HTTPException(status_code=400, detail=str(e))



@router.post('/create-checkout-session')
async def create_checkout_session(request: Request):
    try:
        session = stripe.checkout.Session.create(
            ui_mode = 'embedded',
            line_items=[
                {
                    # Provide the exact Price ID (for example, price_1234) of the product you want to sell
                    'price': 'price_1SKWyKKqzovpZn55fUnIhMhf',
                    'quantity': 1,
                },
            ],
            mode='subscription',
            return_url=YOUR_DOMAIN + '?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"clientSecret": session.client_secret}

@router.get('/session-status')
async def session_status(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        customer_email = None
        if getattr(session, "customer_details", None):
            customer_email = getattr(session.customer_details, "email", None)
        return {
            "status": session.status,
            "customer_email": customer_email
        }
    except stripe.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Checkout session not found.")
    except Exception as e:
        logger.error("Error retrieving checkout session: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post('/cancel-subscription')
async def cancel_subscription(request: Request):
    try:
        data = await request.json()
        subscription_id = data.get('subscriptionId')
        if not subscription_id:
            return JSONResponse(status_code=400, content={"error": "subscriptionId is required"})
        # Cancel the subscription by deleting it
        deleted_subscription = stripe.Subscription.delete(subscription_id)
        # Convert Stripe object to a plain dict for JSON response
        try:
            response_content = deleted_subscription.to_dict()
        except Exception:
            response_content = dict(deleted_subscription)
        return JSONResponse(content=response_content)
    except Exception as e:
        logger.error("Error cancelling subscription: %s", e)
        return JSONResponse(status_code=403, content={"error": str(e)})

