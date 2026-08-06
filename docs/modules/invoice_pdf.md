# `app/invoice_pdf.py`

`generate_invoice_pdf()` builds a one-page PDF with `reportlab`'s low-level `canvas` API
(invoice number, date, customer email, product, amount) and returns it as raw bytes — no
filesystem writes, so it can be stored directly in the `invoices.pdf_bytes` column.
