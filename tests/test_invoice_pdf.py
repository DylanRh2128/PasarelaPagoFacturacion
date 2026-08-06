from datetime import datetime, timezone

from app.invoice_pdf import generate_invoice_pdf


def test_generates_valid_pdf_bytes():
    pdf_bytes = generate_invoice_pdf(
        invoice_number="INV-000001",
        product_name="1-hour consulting session",
        amount_cents=5000,
        currency="usd",
        customer_email="customer@example.com",
        created_at=datetime.now(timezone.utc),
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100
