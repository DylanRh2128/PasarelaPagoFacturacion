# Stripe Checkout + Invoice API

> Also reachable at `/billing` through this portfolio's `portfolio-gateway` reverse proxy,
> which puts all the portfolio's APIs behind one public URL.

## Problem

A small business wants to sell a simple product or service online and hand the customer an
invoice automatically — without building a custom payment form or manually writing PDFs.

## Solution

The API creates a Stripe Checkout Session for one of two fixed-price offerings; Stripe hosts
the entire payment page (card entry, 3D Secure, everything). Once Stripe confirms the payment
via a signed webhook, the API generates a PDF invoice and makes it available for download.
Prices always come from the server's own catalog — never from the client — so nobody can pay a
different amount than what's actually being sold. See
[docs/architecture.md](docs/architecture.md) for the full reasoning.

## Stack

Python + FastAPI + PostgreSQL (SQLAlchemy) + Stripe (Checkout + webhooks) + reportlab (PDF).

## How to run it

```bash
python -m venv .venv
.venv/Scripts/activate        # or source .venv/bin/activate on Linux/Mac
pip install -r requirements.txt

cp .env.example .env          # fill in DATABASE_URL, API_KEY, and your Stripe test keys
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API docs.

To actually receive webhooks locally, use the [Stripe CLI](https://stripe.com/docs/stripe-cli):
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```
It prints a `whsec_...` value — put that in `STRIPE_WEBHOOK_SECRET`. See
[docs/testing.md](docs/testing.md) for a full manual test walkthrough with Stripe's test card.

## Run it with Docker

```bash
docker compose up --build
```
The API is on `http://localhost:8004`. See [docs/deployment.md](docs/deployment.md).

## Try it

```bash
curl -X POST http://localhost:8000/checkout-sessions \
  -H "Content-Type: application/json" \
  -d '{"product_id":"consulting_session","customer_email":"customer@example.com"}'
```

## Documentation

- [docs/architecture.md](docs/architecture.md) — Checkout vs. Payment Intents, server-side pricing, webhook idempotency, junior-acceptable vs. what a senior would do differently
- [docs/api-reference.md](docs/api-reference.md) — endpoints
- [docs/data-model.md](docs/data-model.md) — database schema
- [docs/security.md](docs/security.md) — Stripe key handling, webhook signature verification
- [docs/testing.md](docs/testing.md) — what's tested and why, manual end-to-end test with the Stripe CLI
- [docs/deployment.md](docs/deployment.md) — Docker
