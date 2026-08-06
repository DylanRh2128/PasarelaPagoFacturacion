from types import SimpleNamespace
from unittest.mock import patch


def test_list_payments_without_api_key_returns_401(client):
    response = client.get("/payments")
    assert response.status_code == 401


def test_invoice_pdf_not_found_for_pending_payment(client):
    fake_session = SimpleNamespace(id="cs_pending", url="https://checkout.stripe.com/x")
    with patch("app.checkout.create_checkout_session", return_value=fake_session):
        client.post(
            "/checkout-sessions",
            json={"product_id": "consulting_session", "customer_email": "customer@example.com"},
        )

    payment_id = client.get("/payments", headers={"X-API-Key": "test-api-key"}).json()[0]["id"]
    response = client.get(f"/invoices/{payment_id}/pdf", headers={"X-API-Key": "test-api-key"})
    assert response.status_code == 404


def test_invoice_pdf_not_found_for_unknown_payment(client):
    response = client.get("/invoices/999/pdf", headers={"X-API-Key": "test-api-key"})
    assert response.status_code == 404
