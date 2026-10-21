from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer, Payment
from app.products import UnknownProductError, get_product
from app.schemas import CheckoutRequest, CheckoutResponse
from app.stripe_client import create_checkout_session

router = APIRouter()


@router.post("/checkout-sessions", response_model=CheckoutResponse)
def create_checkout(payload: CheckoutRequest, db: Session = Depends(get_db)):
    try:
        product = get_product(payload.product_id)
    except UnknownProductError as e:
        raise HTTPException(status_code=400, detail=str(e))

    customer = db.query(Customer).filter_by(email=payload.customer_email).first()
    if customer is None:
        customer = Customer(email=payload.customer_email)
        db.add(customer)
        db.flush()

    session = create_checkout_session(payload.product_id, payload.customer_email)

    payment = Payment(
        customer_id=customer.id,
        stripe_checkout_session_id=session.id,
        product_id=payload.product_id,
        amount_cents=product["amount_cents"],
        currency=product["currency"],
        status="pending",
    )
    db.add(payment)
    db.commit()

    return CheckoutResponse(checkout_url=session.url)


# Public on purpose: Checkout session ids are unguessable, and this exposes only the status and
# invoice number — what the success page needs to know the webhook has confirmed the payment.
@router.get("/checkout-sessions/{session_id}")
def get_checkout_status(session_id: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(stripe_checkout_session_id=session_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    return {
        "status": payment.status,
        "invoice_number": payment.invoice.invoice_number if payment.invoice else None,
    }
