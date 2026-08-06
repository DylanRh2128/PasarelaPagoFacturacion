from unittest.mock import patch

import pytest

from app.products import UnknownProductError
from app.stripe_client import create_checkout_session


def test_create_checkout_session_uses_catalog_amount(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("CHECKOUT_SUCCESS_URL", "http://x/ok")
    monkeypatch.setenv("CHECKOUT_CANCEL_URL", "http://x/cancel")

    with patch("stripe.checkout.Session.create") as mocked_create:
        create_checkout_session("consulting_session", "customer@example.com")

    _, kwargs = mocked_create.call_args
    assert kwargs["line_items"][0]["price_data"]["unit_amount"] == 5000
    assert kwargs["line_items"][0]["price_data"]["currency"] == "usd"


def test_unknown_product_never_calls_stripe():
    with patch("stripe.checkout.Session.create") as mocked_create:
        with pytest.raises(UnknownProductError):
            create_checkout_session("not-a-real-product", "customer@example.com")

    mocked_create.assert_not_called()
