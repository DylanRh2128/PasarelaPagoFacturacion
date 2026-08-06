import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_invoice_pdf(
    invoice_number: str,
    product_name: str,
    amount_cents: int,
    currency: str,
    customer_email: str,
    created_at,
) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, 720, "INVOICE")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, 690, f"Invoice number: {invoice_number}")
    pdf.drawString(72, 674, f"Date: {created_at:%Y-%m-%d}")
    pdf.drawString(72, 658, f"Billed to: {customer_email}")

    pdf.drawString(72, 610, f"Item: {product_name}")
    pdf.drawString(72, 594, f"Amount: {amount_cents / 100:.2f} {currency.upper()}")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
