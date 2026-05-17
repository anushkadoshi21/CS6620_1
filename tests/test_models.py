from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.client import ClientCreate, ClientResponse, ClientUpdate
from app.models.health import HealthResponse


class TestClientCreate:
    def test_valid_payload(self):
        c = ClientCreate(
            name="Acme",
            organization_type="Enterprise",
            total_headcount=10,
            joined_at=datetime(2024, 1, 1),
            total_valuation=1_000_000.0,
            billed_amount=5000.0,
            amount_paid=2500.0,
        )
        assert c.name == "Acme"
        assert c.latest_transaction_date is None

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            ClientCreate(
                organization_type="Enterprise",
                total_headcount=10,
                joined_at=datetime(2024, 1, 1),
                total_valuation=1_000_000.0,
                billed_amount=5000.0,
                amount_paid=2500.0,
            )

    def test_negative_headcount_rejected(self):
        with pytest.raises(ValidationError):
            ClientCreate(
                name="Acme",
                organization_type="Enterprise",
                total_headcount=-1,
                joined_at=datetime(2024, 1, 1),
                total_valuation=1_000_000.0,
                billed_amount=5000.0,
                amount_paid=2500.0,
            )

    def test_negative_money_fields_rejected(self):
        for field in ("total_valuation", "billed_amount", "amount_paid"):
            base = dict(
                name="Acme",
                organization_type="Enterprise",
                total_headcount=10,
                joined_at=datetime(2024, 1, 1),
                total_valuation=1_000_000.0,
                billed_amount=5000.0,
                amount_paid=2500.0,
            )
            base[field] = -1.0
            with pytest.raises(ValidationError):
                ClientCreate(**base)


class TestClientUpdate:
    def test_all_fields_optional(self):
        u = ClientUpdate()
        assert u.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        u = ClientUpdate(name="New Name", total_headcount=50)
        assert u.model_dump(exclude_unset=True) == {
            "name": "New Name",
            "total_headcount": 50,
        }

    def test_negative_value_rejected(self):
        with pytest.raises(ValidationError):
            ClientUpdate(billed_amount=-10.0)


class TestClientResponse:
    def test_auto_generates_uuid(self):
        c = ClientResponse(
            name="Acme",
            organization_type="Enterprise",
            total_headcount=10,
            joined_at=datetime(2024, 1, 1),
            total_valuation=1_000_000.0,
            billed_amount=5000.0,
            amount_paid=2500.0,
        )
        assert isinstance(c.id, UUID)


class TestHealthResponse:
    def test_valid(self):
        h = HealthResponse(status="ok", timestamp="2026-05-16T00:00:00", service="x")
        assert h.status == "ok"
