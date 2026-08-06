PRODUCTS = {
    "consulting_session": {"name": "1-hour consulting session", "amount_cents": 5000, "currency": "usd"},
    "report_generation": {"name": "Custom report generation", "amount_cents": 2000, "currency": "usd"},
}


class UnknownProductError(ValueError):
    pass


def get_product(product_id: str) -> dict:
    if product_id not in PRODUCTS:
        raise UnknownProductError(f"Unknown product_id {product_id!r}. Allowed: {sorted(PRODUCTS)}")
    return PRODUCTS[product_id]
