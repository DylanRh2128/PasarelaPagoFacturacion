from fastapi import FastAPI

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
