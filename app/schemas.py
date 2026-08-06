from datetime import datetime

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    product_id: str
    customer_email: str


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
