# Architecture

## Flow

`POST /checkout-sessions` → `app/products.py` looks up the price (never trusts a client-sent
amount) → gets/creates a `Customer` → `app/stripe_client.py` creates a Stripe Checkout Session →
a `Payment` row is persisted as `pending` → the checkout URL is returned. The customer pays on
Stripe's hosted page. Stripe calls `POST /webhooks/stripe` → signature is verified →
`app/invoice_pdf.py` generates the PDF → an `Invoice` row is persisted, `Payment.status` becomes
`succeeded`. `GET /invoices/{payment_id}/pdf` serves the stored bytes back.

## Why Stripe Checkout, not Payment Intents + a custom form

Payment Intents would require building and hosting a card-collection form (Stripe Elements),
which is frontend work outside this portfolio's backend focus and duplicates something Stripe
already does well — hosted, PCI-compliant, handles 3D Secure automatically. Checkout Session is
the right-sized tool: this API's job is deciding *what* is being sold and *reacting* to a
completed payment, not re-implementing a payment form.

## Prices always come from the server

`app/products.py` is a fixed dictionary — `product_id → (name, amount_cents, currency)`. The
client only ever sends a `product_id`; the amount charged is looked up server-side and passed to
Stripe directly. This is the direct answer to the idea's security question about validating
amounts server-side: there is no code path where a client-supplied number becomes a charge
amount.

## Webhook signature verification and idempotency

`app/webhooks.py` calls `stripe.Webhook.construct_event()`, which verifies the `Stripe-Signature`
header cryptographically before trusting anything in the payload — an unsigned or wrongly-signed
request is rejected with `400` before touching the database. Stripe also retries webhook
deliveries, so the handler checks `Payment.status` first: if it's already `succeeded`, the event
is a no-op (`{"status": "ignored"}`) instead of generating a second invoice. `Invoice.payment_id`
is also a unique column — a defense-in-depth backstop against a duplicate ever being written.

## PDF stored as bytes in Postgres, not object storage

`Invoice.pdf_bytes` is a `LargeBinary` column. Junior-acceptable for this MVP's volume — zero
extra infrastructure, one less credential to manage. What a senior would do differently at real
scale: move PDFs to object storage (S3, or this portfolio's own `AlmacenamientoCDN` project) and
store only a reference in Postgres, since large binary blobs bloat database backups and slow
down queries on the table over time. Deliberately not wired to `AlmacenamientoCDN` here — each
portfolio project stays self-contained rather than depending on another one.

## Junior-acceptable vs. what a senior would do differently

- **Schema management**: `Base.metadata.create_all()` on startup, no Alembic — consistent with
  the rest of this portfolio.
- **Single API key for all admin endpoints**: fine for one operator; a senior serving multiple
  staff members would want per-user credentials and an audit trail of who downloaded what.
- **No customer self-service invoice download**: customers get their receipt from Stripe itself
  (Checkout can email one); this API's own invoice endpoint is admin-only. A real product would
  need a customer-facing auth system to let customers fetch their own invoices — out of scope
  for this MVP.
