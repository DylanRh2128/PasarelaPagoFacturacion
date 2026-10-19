# API Reference

## `POST /checkout-sessions`

Public. Body:
```json
{"product_id": "consulting_session", "customer_email": "customer@example.com"}
```
`product_id` is one of `consulting_session` ($50.00) or `report_generation` ($20.00) — see
`app/products.py`.

Response `200`: `{"checkout_url": "https://checkout.stripe.com/..."}`. `400` if `product_id`
isn't in the catalog.

## `POST /webhooks/stripe`

Called by Stripe, not by a human. Requires a valid `Stripe-Signature` header (`400` if missing
or invalid). Only reacts to `checkout.session.completed`; anything else is acknowledged and
ignored. Always returns `200` for a request it can process (including a duplicate/already-
processed event) so Stripe doesn't keep retrying — only a genuinely invalid signature gets a
non-200.

## `GET /payments`

Requires `X-API-Key`. Lists all payments, most recent first, with their status
(`pending`/`succeeded`).

## `GET /invoices/{payment_id}/pdf`

Requires `X-API-Key`. Returns the invoice as `application/pdf`. `404` if the payment doesn't
exist or hasn't succeeded yet (no invoice has been generated).

## `GET /checkout-success` and `GET /checkout-cancelled`

Plain HTML pages Stripe redirects the buyer to (point `CHECKOUT_SUCCESS_URL` /
`CHECKOUT_CANCEL_URL` at them). Informational only — a payment counts as paid when the webhook
says so, never because someone opened the success page.
