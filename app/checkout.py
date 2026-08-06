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
