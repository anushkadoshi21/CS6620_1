from datetime import datetime
from uuid import UUID, uuid4

from app.constants import DUMMY_CLIENTS
from app.models.client import ClientCreate, ClientUpdate
from app.services.client_service import ClientService


def _make_create() -> ClientCreate:
    return ClientCreate(
        name="New Client",
        organization_type="SaaS",
        total_headcount=15,
        joined_at=datetime(2025, 2, 1),
        total_valuation=3_000_000.0,
        billed_amount=8000.0,
        amount_paid=4000.0,
    )


class TestListClients:
    def test_returns_seeded_clients(self):
        result = ClientService.list_clients()
        assert len(result) == len(DUMMY_CLIENTS)


class TestGetClient:
    def test_returns_existing(self):
        existing_id = DUMMY_CLIENTS[0].id
        result = ClientService.get_client(existing_id)
        assert result is not None
        assert result.id == existing_id

    def test_returns_none_for_missing(self):
        assert ClientService.get_client(uuid4()) is None


class TestCreateClient:
    def test_assigns_id_and_persists(self):
        created = ClientService.create_client(_make_create())
        assert isinstance(created.id, UUID)
        assert ClientService.get_client(created.id) == created

    def test_increases_count(self):
        before = len(ClientService.list_clients())
        ClientService.create_client(_make_create())
        assert len(ClientService.list_clients()) == before + 1


class TestUpdateClient:
    def test_partial_update_preserves_unchanged_fields(self):
        target = DUMMY_CLIENTS[0]
        updated = ClientService.update_client(
            target.id, ClientUpdate(name="Renamed")
        )
        assert updated is not None
        assert updated.name == "Renamed"
        assert updated.organization_type == target.organization_type
        assert updated.total_headcount == target.total_headcount

    def test_returns_none_for_missing(self):
        assert ClientService.update_client(uuid4(), ClientUpdate(name="x")) is None

    def test_can_set_latest_transaction_date(self):
        target_id = DUMMY_CLIENTS[4].id  # seed has None here
        ts = datetime(2026, 5, 16, 9, 0, 0)
        updated = ClientService.update_client(
            target_id, ClientUpdate(latest_transaction_date=ts)
        )
        assert updated.latest_transaction_date == ts


class TestDeleteClient:
    def test_removes_existing(self):
        target_id = DUMMY_CLIENTS[0].id
        assert ClientService.delete_client(target_id) is True
        assert ClientService.get_client(target_id) is None

    def test_returns_false_for_missing(self):
        assert ClientService.delete_client(uuid4()) is False
