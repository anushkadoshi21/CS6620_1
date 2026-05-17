import pytest
from fastapi.testclient import TestClient

from app.constants import DUMMY_CLIENTS
from app.main import app
from app.services.client_service import ClientService


@pytest.fixture(autouse=True)
def reset_client_store():
    """Reseed the in-memory client store before every test."""
    ClientService._clients = {c.id: c.model_copy(deep=True) for c in DUMMY_CLIENTS}
    yield
    ClientService._clients = {c.id: c.model_copy(deep=True) for c in DUMMY_CLIENTS}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_client_payload():
    return {
        "name": "Test Co",
        "organization_type": "Startup",
        "total_headcount": 25,
        "joined_at": "2025-01-15T10:00:00",
        "total_valuation": 5000000.0,
        "billed_amount": 10000.0,
        "amount_paid": 7500.0,
        "latest_transaction_date": "2026-05-01T12:00:00",
    }
