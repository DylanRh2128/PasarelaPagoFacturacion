# Security

## Secrets

`DATABASE_URL`, `API_KEY`, `STRIPE_SECRET_KEY`, and `STRIPE_WEBHOOK_SECRET` are environment
variables (`.env`, git-ignored; only `.env.example` with placeholders is committed).
`STRIPE_SECRET_KEY` can create real charges against your Stripe account — never commit it, never
log it, never put it in a frontend. Use a `sk_test_...` key for all development.

## Webhook signature verification

`POST /webhooks/stripe` calls `stripe.Webhook.construct_event()` with `STRIPE_WEBHOOK_SECRET`,
which verifies the `Stripe-Signature` header using HMAC-SHA256 before anything in the payload is
trusted. Without this, anyone could `POST` a fake "payment succeeded" event and get a free
invoice generated. Get `STRIPE_WEBHOOK_SECRET` either from the Stripe Dashboard (for a real
deployed endpoint) or from `stripe listen` (for local testing — see `docs/testing.md`).

## Server-side pricing

`app/products.py` is the only source of truth for what something costs. `POST /checkout-sessions`
takes a `product_id`, never an amount — see `docs/architecture.md` for why this closes off the
most obvious way someone could try to pay less than the real price.

## Idempotency

Stripe webhooks can be delivered more than once for the same event. `app/webhooks.py` checks
whether the matching `Payment` is already `succeeded` before doing anything, and `Invoice` has a
unique constraint on `payment_id` as a backstop — a duplicate delivery never creates a second
invoice or double-charges anything on our side (Stripe itself only charges the customer once;
this is about our own side effects).
