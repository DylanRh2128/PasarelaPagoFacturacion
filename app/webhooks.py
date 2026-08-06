import os

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.invoice_pdf import generate_invoice_pdf
from app.models import Invoice, Payment
from app.products import get_product

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {e}")

    if event["type"] != "checkout.session.completed":
        return {"status": "ignored"}

    session = event["data"]["object"]
    payment = db.query(Payment).filter_by(stripe_checkout_session_id=session["id"]).first()
    if payment is None or payment.status == "succeeded":
        return {"status": "ignored"}  # unknown session, or already processed (idempotent)

    payment.status = "succeeded"
    invoice_number = f"INV-{payment.id:06d}"
    pdf_bytes = generate_invoice_pdf(
        invoice_number=invoice_number,
        product_name=get_product(payment.product_id)["name"],
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        customer_email=payment.customer.email,
        created_at=payment.created_at,
    )
    db.add(Invoice(payment_id=payment.id, invoice_number=invoice_number, pdf_bytes=pdf_bytes))
    db.commit()

    return {"status": "processed"}
