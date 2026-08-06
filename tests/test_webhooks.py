import json
from types import SimpleNamespace
from unittest.mock import patch

from tests.conftest import sign_stripe_payload

HEADERS = {"X-API-Key": "test-api-key"}


def _checkout_completed_event(session_id: str) -> bytes:
    return json.dumps(
        {
            "id": "evt_test_1",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {"object": {"id": session_id}},
        }
    ).encode()


def _create_pending_payment(client, session_id="cs_test_123"):
    fake_session = SimpleNamespace(id=session_id, url="https://checkout.stripe.com/x")
    with patch("app.checkout.create_checkout_session", return_value=fake_session):
        client.post(
            "/checkout-sessions",
            json={"product_id": "consulting_session", "customer_email": "customer@example.com"},
        )


def test_webhook_marks_payment_succeeded_and_creates_invoice(client):
    _create_pending_payment(client)
    payload = _checkout_completed_event("cs_test_123")

    response = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": sign_stripe_payload(payload)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"

    payments = client.get("/payments", headers=HEADERS).json()
    assert payments[0]["status"] == "succeeded"

    pdf_response = client.get(f"/invoices/{payments[0]['id']}/pdf", headers=HEADERS)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"


def test_webhook_invalid_signature_returns_400(client):
    payload = _checkout_completed_event("cs_test_123")
    response = client.post(
        "/webhooks/stripe", content=payload, headers={"stripe-signature": "t=1,v1=wrongsig"}
    )
    assert response.status_code == 400


def test_webhook_is_idempotent_on_duplicate_event(client):
    _create_pending_payment(client)
    payload = _checkout_completed_event("cs_test_123")
    headers = {"stripe-signature": sign_stripe_payload(payload)}

    client.post("/webhooks/stripe", content=payload, headers=headers)
    second_response = client.post("/webhooks/stripe", content=payload, headers=headers)

    assert second_response.json()["status"] == "ignored"

    # The unique constraint on Invoice.payment_id would raise if a second invoice had been
    # inserted; reaching here at all proves the duplicate event never tried to create one.
    payment_id = client.get("/payments", headers=HEADERS).json()[0]["id"]
    assert client.get(f"/invoices/{payment_id}/pdf", headers=HEADERS).status_code == 200
