from datetime import datetime
from uuid import UUID

from app.models.client import ClientResponse


DUMMY_CLIENTS: list[ClientResponse] = [
    ClientResponse(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        name="Acme Corp",
        organization_type="Enterprise",
        total_headcount=1200,
        joined_at=datetime(2021, 3, 14, 9, 0, 0),
        total_valuation=85_000_000.00,
        billed_amount=240_000.00,
        amount_paid=200_000.00,
        latest_transaction_date=datetime(2026, 4, 28, 15, 30, 0),
    ),
    ClientResponse(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Globex Industries",
        organization_type="Manufacturing",
        total_headcount=540,
        joined_at=datetime(2022, 7, 1, 10, 30, 0),
        total_valuation=32_500_000.00,
        billed_amount=120_000.00,
        amount_paid=120_000.00,
        latest_transaction_date=datetime(2026, 5, 2, 11, 0, 0),
    ),
    ClientResponse(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        name="Initech",
        organization_type="SaaS",
        total_headcount=85,
        joined_at=datetime(2023, 11, 9, 8, 15, 0),
        total_valuation=12_000_000.00,
        billed_amount=45_000.00,
        amount_paid=30_000.00,
        latest_transaction_date=datetime(2026, 5, 10, 16, 45, 0),
    ),
    ClientResponse(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        name="Umbrella Health",
        organization_type="Healthcare",
        total_headcount=2100,
        joined_at=datetime(2020, 1, 22, 12, 0, 0),
        total_valuation=150_000_000.00,
        billed_amount=410_000.00,
        amount_paid=390_000.00,
        latest_transaction_date=datetime(2026, 4, 15, 9, 20, 0),
    ),
    ClientResponse(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        name="Stark Robotics",
        organization_type="Startup",
        total_headcount=42,
        joined_at=datetime(2024, 6, 5, 14, 0, 0),
        total_valuation=8_500_000.00,
        billed_amount=18_000.00,
        amount_paid=9_000.00,
        latest_transaction_date=None,
    ),
]
