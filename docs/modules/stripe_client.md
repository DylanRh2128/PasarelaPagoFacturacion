# `app/stripe_client.py`

`create_checkout_session()` looks up the product in `app/products.py` first (so an unknown
product never reaches Stripe), then creates a Stripe Checkout Session with the amount taken
directly from the catalog.
