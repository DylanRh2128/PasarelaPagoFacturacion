# Testing

Run with: `pytest` (needs `DATABASE_URL`, `API_KEY`, `STRIPE_SECRET_KEY`,
`STRIPE_WEBHOOK_SECRET`, `CHECKOUT_SUCCESS_URL`, `CHECKOUT_CANCEL_URL` set to any dummy value —
tests never call the real Stripe API).

- `tests/test_invoice_pdf.py` — the generated PDF starts with the `%PDF` signature and has a
  reasonable size.
- `tests/test_stripe_client.py` — `create_checkout_session` passes the catalog's amount (never
  an arbitrary one) to Stripe; an unknown product raises before Stripe is ever called.
- `tests/test_checkout_api.py` — happy path (Stripe mocked), invalid product → `400`, and
  repeat customers reuse the same `Customer` row instead of creating duplicates.
- `tests/test_webhooks.py` — a fake Stripe event is signed by hand in `tests/conftest.py`'s
  `sign_stripe_payload()`, replicating Stripe's own `t={timestamp},v1={hmac-sha256}` scheme, so
  the real signature-verification code path is exercised without ever touching Stripe. Covers: a
  validly-signed event marks the payment succeeded and creates a downloadable invoice; an
  invalid signature → `400`; the same event delivered twice → the second delivery is a no-op
  (idempotency).
- `tests/test_payments_api.py` — missing `X-API-Key` → `401`; requesting an invoice for a
  pending (not yet paid) or nonexistent payment → `404`.

## Manual end-to-end test (not automated — needs a real Stripe test account)

1. `stripe listen --forward-to localhost:8000/webhooks/stripe`, copy the `whsec_...` it prints
   into `STRIPE_WEBHOOK_SECRET`.
2. `POST /checkout-sessions` with a valid `product_id`, open the returned `checkout_url`.
3. Pay with Stripe's test card `4242 4242 4242 4242`, any future expiry, any CVC.
4. Confirm `GET /payments` shows `status: succeeded` and
   `GET /invoices/{id}/pdf` downloads a real invoice.
