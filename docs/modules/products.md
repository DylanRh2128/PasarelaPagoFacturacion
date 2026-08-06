# `app/products.py`

The fixed product catalog — the single source of truth for what each `product_id` costs.
`get_product()` raises `UnknownProductError` for anything not in the catalog, checked before any
Stripe or database call happens.
