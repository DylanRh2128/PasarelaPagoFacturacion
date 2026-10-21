from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    product_id: str
    customer_email: str
    language: Literal["en", "es"] = "en"  # language of Stripe's hosted checkout page


class CheckoutResponse(BaseModel):
    checkout_url: str


class PaymentOut(BaseModel):
    id: int
    created_at: datetime
    product_id: str
    amount_cents: int
    currency: str
    status: str

    model_config = {"from_attributes": True}
