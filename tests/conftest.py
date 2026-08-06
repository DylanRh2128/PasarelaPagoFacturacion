import hashlib
import hmac
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 — registers models on Base before create_all
from app.db import Base, get_db
from app.main import app

API_KEY = "test-api-key"
WEBHOOK_SECRET = "whsec_test_secret"


def sign_stripe_payload(payload: bytes, secret: str = WEBHOOK_SECRET, timestamp: int | None = None) -> str:
    timestamp = timestamp or int(time.time())
    signed_payload = f"{timestamp}.".encode() + payload
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
