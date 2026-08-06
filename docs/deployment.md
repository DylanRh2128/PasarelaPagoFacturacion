# Deployment

## Docker (local)

```bash
docker compose up --build
```
(with `API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `CHECKOUT_SUCCESS_URL`,
`CHECKOUT_CANCEL_URL` set in your shell or a `.env` next to `docker-compose.yml`)

Two containers: `api` (port `8004` on the host) and `db` (`postgres:16-alpine`, port `5543` on
the host, with a healthcheck `api` waits on). `DATABASE_URL` inside `docker-compose.yml` points
at `db:5432` by Docker network name, separate from the `localhost`-based value in
`.env.example`.

## Why Docker, no Kubernetes

Same reasoning as the rest of this portfolio: one service, one database — no scaling problem
that would justify Kubernetes' complexity here.

## Deploying beyond local Docker

The `Dockerfile` is what Railway/Render would build directly. After deploying, update the
webhook endpoint URL in the Stripe Dashboard (Developers → Webhooks) to point at the deployed
`/webhooks/stripe` URL, and use the signing secret Stripe generates for *that* endpoint as
`STRIPE_WEBHOOK_SECRET` — it's different from the one `stripe listen` gives you locally.
