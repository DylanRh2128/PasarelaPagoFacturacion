# `app/checkout.py`

`POST /checkout-sessions`: validates the product, reuses an existing `Customer` by email if one
exists (rather than creating duplicates for repeat buyers), creates the Stripe session, and
persists a `pending` `Payment` — all before returning the checkout URL to the caller.
