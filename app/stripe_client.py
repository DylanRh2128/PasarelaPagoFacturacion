import os

import stripe

from app.products import get_product


def create_checkout_session(product_id: str, customer_email: str):
    product = get_product(product_id)  # raises UnknownProductError before calling Stripe

    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    return stripe.checkout.Session.create(
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "price_data": {
                    "currency": product["currency"],
                    "unit_amount": product["amount_cents"],
                    "product_data": {"name": product["name"]},
                },
                "quantity": 1,
            }
        ],
        # Stripe fills in {CHECKOUT_SESSION_ID}, so the success page can wait for the webhook.
        success_url=os.environ["CHECKOUT_SUCCESS_URL"] + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=os.environ["CHECKOUT_CANCEL_URL"],
    )
