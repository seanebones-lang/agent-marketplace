"""
Billing API Endpoints

This module provides Stripe billing integration for subscriptions and payments.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import stripe
import os

from database import get_db
from models.customer import Customer
from core.security import verify_bearer_token
from core.config import settings
from core.logging import get_logger


router = APIRouter(prefix="/billing", tags=["Billing"])
logger = get_logger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


class CreateCheckoutSessionRequest(BaseModel):
    """Create checkout session request"""
    price_id: str
    success_url: str
    cancel_url: str


class CreateCheckoutSessionResponse(BaseModel):
    """Create checkout session response"""
    session_id: str
    url: str


class SubscriptionInfo(BaseModel):
    """Subscription information"""
    id: str
    status: str
    current_period_start: int
    current_period_end: int
    cancel_at_period_end: bool
    plan_name: str
    plan_amount: float


class PaymentMethod(BaseModel):
    """Payment method information"""
    id: str
    type: str
    card_brand: Optional[str]
    card_last4: Optional[str]
    card_exp_month: Optional[int]
    card_exp_year: Optional[int]


class Invoice(BaseModel):
    """Invoice information"""
    id: str
    amount_due: float
    amount_paid: float
    status: str
    created: int
    invoice_pdf: Optional[str]


class UsageRecord(BaseModel):
    """Usage record for metered billing"""
    quantity: int
    timestamp: int
    action: str = "increment"


@router.post("/checkout/session", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription.
    
    Args:
        request: Checkout session request
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Checkout session information
        
    Raises:
        HTTPException: If session creation fails
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        # Create or retrieve Stripe customer
        if not hasattr(customer, 'stripe_customer_id') or not customer.stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                email=customer.email,
                name=customer.name,
                metadata={"customer_id": customer.id}
            )
            customer.stripe_customer_id = stripe_customer.id
            db.commit()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": request.price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "customer_id": customer.id
            }
        )
        
        logger.info(f"Created checkout session for customer {customer.id}")
        
        return CreateCheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get current subscription information.
    
    Args:
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Subscription information
        
    Raises:
        HTTPException: If no subscription found
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        raise HTTPException(status_code=404, detail="No subscription found")
    
    try:
        # Get subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer.stripe_customer_id,
            limit=1
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=404, detail="No active subscription")
        
        sub = subscriptions.data[0]
        
        return SubscriptionInfo(
            id=sub.id,
            status=sub.status,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            plan_name=sub.plan.nickname or sub.plan.id,
            plan_amount=sub.plan.amount / 100.0
        )
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription/cancel")
async def cancel_subscription(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription at period end.
    
    Args:
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If cancellation fails
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        raise HTTPException(status_code=404, detail="No subscription found")
    
    try:
        # Get active subscription
        subscriptions = stripe.Subscription.list(
            customer=customer.stripe_customer_id,
            status="active",
            limit=1
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=404, detail="No active subscription")
        
        # Cancel at period end
        subscription = stripe.Subscription.modify(
            subscriptions.data[0].id,
            cancel_at_period_end=True
        )
        
        logger.info(f"Cancelled subscription for customer {customer.id}")
        
        return {
            "message": "Subscription will be cancelled at period end",
            "cancel_at": subscription.current_period_end
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription/resume")
async def resume_subscription(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Resume a cancelled subscription.
    
    Args:
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Success message
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        raise HTTPException(status_code=404, detail="No subscription found")
    
    try:
        # Get subscription
        subscriptions = stripe.Subscription.list(
            customer=customer.stripe_customer_id,
            limit=1
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=404, detail="No subscription found")
        
        # Resume subscription
        subscription = stripe.Subscription.modify(
            subscriptions.data[0].id,
            cancel_at_period_end=False
        )
        
        logger.info(f"Resumed subscription for customer {customer.id}")
        
        return {"message": "Subscription resumed successfully"}
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payment-methods", response_model=List[PaymentMethod])
async def get_payment_methods(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get customer payment methods.
    
    Args:
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        List of payment methods
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        return []
    
    try:
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.stripe_customer_id,
            type="card"
        )
        
        return [
            PaymentMethod(
                id=pm.id,
                type=pm.type,
                card_brand=pm.card.brand if pm.card else None,
                card_last4=pm.card.last4 if pm.card else None,
                card_exp_month=pm.card.exp_month if pm.card else None,
                card_exp_year=pm.card.exp_year if pm.card else None
            )
            for pm in payment_methods.data
        ]
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return []


@router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    limit: int = 10,
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get customer invoices.
    
    Args:
        limit: Maximum number of invoices to return
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        List of invoices
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        return []
    
    try:
        invoices = stripe.Invoice.list(
            customer=customer.stripe_customer_id,
            limit=limit
        )
        
        return [
            Invoice(
                id=inv.id,
                amount_due=inv.amount_due / 100.0,
                amount_paid=inv.amount_paid / 100.0,
                status=inv.status,
                created=inv.created,
                invoice_pdf=inv.invoice_pdf
            )
            for inv in invoices.data
        ]
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return []


@router.post("/usage/record")
async def record_usage(
    usage: UsageRecord,
    subscription_item_id: str,
    token_data: dict = Depends(verify_bearer_token)
):
    """
    Record usage for metered billing.
    
    Args:
        usage: Usage record
        subscription_item_id: Stripe subscription item ID
        token_data: Decoded JWT token
        
    Returns:
        Usage record confirmation
    """
    try:
        usage_record = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=usage.quantity,
            timestamp=usage.timestamp,
            action=usage.action
        )
        
        logger.info(f"Recorded usage: {usage.quantity} units")
        
        return {
            "id": usage_record.id,
            "quantity": usage_record.quantity,
            "timestamp": usage_record.timestamp
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    
    Args:
        request: FastAPI request
        db: Database session
        
    Returns:
        Success response
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event.type == "checkout.session.completed":
        session = event.data.object
        logger.info(f"Checkout completed: {session.id}")
        
        # Update customer subscription status
        customer_id = session.metadata.get("customer_id")
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
            if customer:
                customer.tier = "pro"  # Update based on subscription
                db.commit()
    
    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        logger.info(f"Subscription deleted: {subscription.id}")
        
        # Downgrade customer tier
        stripe_customer_id = subscription.customer
        customer = db.query(Customer).filter(
            Customer.stripe_customer_id == stripe_customer_id
        ).first()
        if customer:
            customer.tier = "free"
            db.commit()
    
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        logger.warning(f"Payment failed: {invoice.id}")
        
        # Handle failed payment (send notification, etc.)
    
    return {"status": "success"}


@router.get("/portal")
async def create_portal_session(
    return_url: str,
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Create Stripe customer portal session.
    
    Args:
        return_url: URL to return to after portal session
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Portal session URL
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer or not hasattr(customer, 'stripe_customer_id'):
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer.stripe_customer_id,
            return_url=return_url
        )
        
        return {"url": session.url}
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

