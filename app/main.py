from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.checkout import router as checkout_router
from app.db import Base, engine
from app import models  # noqa: F401 — registers models on Base before create_all
from app.payments import router as payments_router
from app.webhooks import router as webhooks_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stripe Checkout + Invoice API")
app.include_router(checkout_router)
app.include_router(webhooks_router)
app.include_router(payments_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Where Stripe Checkout sends the buyer back (CHECKOUT_SUCCESS_URL / CHECKOUT_CANCEL_URL).
# The payment itself is confirmed by the webhook, not by landing here.
@app.get("/checkout-success", response_class=HTMLResponse)
def checkout_success():
    return "<h1>Payment received</h1><p>Your invoice is generated once Stripe confirms the payment.</p>"


@app.get("/checkout-cancelled", response_class=HTMLResponse)
def checkout_cancelled():
    return "<h1>Payment cancelled</h1><p>No charge was made.</p>"
