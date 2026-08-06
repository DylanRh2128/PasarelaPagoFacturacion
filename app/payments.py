from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.auth import verify_api_key
from app.db import get_db
from app.models import Invoice, Payment
from app.schemas import PaymentOut

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return db.query(Payment).order_by(Payment.created_at.desc()).all()


@router.get("/invoices/{payment_id}/pdf")
def download_invoice_pdf(payment_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter_by(payment_id=payment_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found for this payment")

    return Response(
        content=invoice.pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{invoice.invoice_number}.pdf"'},
    )
