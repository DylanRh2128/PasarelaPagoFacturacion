from types import SimpleNamespace
from unittest.mock import patch


def fake_session(session_id="cs_test_123"):
    return SimpleNamespace(id=session_id, url=f"https://checkout.stripe.com/{session_id}")


def test_create_checkout_happy_path(client):
    with patch("app.checkout.create_checkout_session", return_value=fake_session()):
        response = client.post(
            "/checkout-sessions",
            json={"product_id": "consulting_session", "customer_email": "customer@example.com"},
        )

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://checkout.stripe.com/cs_test_123"


def test_create_checkout_invalid_product_returns_400(client):
    with patch("app.checkout.create_checkout_session") as mocked:
        response = client.post(
            "/checkout-sessions",
            json={"product_id": "not-a-real-product", "customer_email": "customer@example.com"},
        )
        mocked.assert_not_called()

    assert response.status_code == 400


def test_create_checkout_reuses_existing_customer(client):
    with patch("app.checkout.create_checkout_session", side_effect=[fake_session("cs_1"), fake_session("cs_2")]):
        client.post(
            "/checkout-sessions",
            json={"product_id": "consulting_session", "customer_email": "repeat@example.com"},
        )
        client.post(
            "/checkout-sessions",
            json={"product_id": "report_generation", "customer_email": "repeat@example.com"},
        )

    with patch("app.checkout.create_checkout_session") as _:
        response = client.get("/payments", headers={"X-API-Key": "test-api-key"})
    assert len(response.json()) == 2
