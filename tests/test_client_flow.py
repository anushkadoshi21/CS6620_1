"""Scenario tests: each function walks through a sequence of operations
where later steps depend on earlier ones. The autouse fixture in conftest
still reseeds before each scenario so scenarios stay independent of each
other — but within a scenario, state accumulates."""

from app.constants import DUMMY_CLIENTS


class TestClientLifecycleFlow:
    def test_create_read_update_delete(self, client, sample_client_payload):
        # Start from seeded state
        initial = client.get("/clients").json()
        assert len(initial) == len(DUMMY_CLIENTS)

        # Create a new client
        created = client.post("/clients", json=sample_client_payload)
        assert created.status_code == 201
        new_id = created.json()["id"]

        # List now reflects the new client
        after_create = client.get("/clients").json()
        assert len(after_create) == len(DUMMY_CLIENTS) + 1
        assert new_id in {c["id"] for c in after_create}

        # Read the new client by id
        fetched = client.get(f"/clients/{new_id}")
        assert fetched.status_code == 200
        assert fetched.json()["name"] == sample_client_payload["name"]

        # Partially update it
        updated = client.patch(
            f"/clients/{new_id}",
            json={"amount_paid": 9500.0, "total_headcount": 40},
        )
        assert updated.status_code == 200
        assert updated.json()["amount_paid"] == 9500.0
        assert updated.json()["total_headcount"] == 40
        # Untouched field still matches original payload
        assert updated.json()["organization_type"] == sample_client_payload["organization_type"]

        # Delete it
        deleted = client.delete(f"/clients/{new_id}")
        assert deleted.status_code == 204

        # Verify it's gone and list is back to seed size
        gone = client.get(f"/clients/{new_id}")
        assert gone.status_code == 404
        assert len(client.get("/clients").json()) == len(DUMMY_CLIENTS)


class TestMultiClientFlow:
    def test_mixed_operations_across_seed_and_new(self, client):
        # Seeded client we'll mutate
        seeded = DUMMY_CLIENTS[2]

        # Add two new clients
        payloads = [
            {
                "name": f"Flow Co {i}",
                "organization_type": "SaaS",
                "total_headcount": 10 + i,
                "joined_at": "2025-03-01T09:00:00",
                "total_valuation": 1_000_000.0 * (i + 1),
                "billed_amount": 5000.0,
                "amount_paid": 2500.0,
            }
            for i in range(2)
        ]
        new_ids = [client.post("/clients", json=p).json()["id"] for p in payloads]
        assert len(new_ids) == 2

        # Rename the seeded client
        renamed = client.patch(
            f"/clients/{seeded.id}", json={"name": "Renamed Seed"}
        )
        assert renamed.status_code == 200
        assert renamed.json()["name"] == "Renamed Seed"

        # Delete one of the new clients
        assert client.delete(f"/clients/{new_ids[0]}").status_code == 204

        # Final state: seed_count + 1
        final = client.get("/clients").json()
        assert len(final) == len(DUMMY_CLIENTS) + 1

        names_by_id = {c["id"]: c["name"] for c in final}
        assert names_by_id[str(seeded.id)] == "Renamed Seed"
        assert names_by_id[new_ids[1]] == "Flow Co 1"
        assert new_ids[0] not in names_by_id

        # Other seeded clients are untouched
        untouched = DUMMY_CLIENTS[0]
        assert names_by_id[str(untouched.id)] == untouched.name


class TestPaymentProgressionFlow:
    def test_billing_then_payments_then_transaction_update(self, client):
        target = DUMMY_CLIENTS[4]  

        # Confirm starting state
        start = client.get(f"/clients/{target.id}").json()
        assert start["latest_transaction_date"] is None
        starting_paid = start["amount_paid"]

        # Bill more
        new_billed = start["billed_amount"] + 5000.0
        r = client.patch(
            f"/clients/{target.id}", json={"billed_amount": new_billed}
        )
        assert r.status_code == 200
        assert r.json()["billed_amount"] == new_billed
        # amount_paid hasn't moved yet
        assert r.json()["amount_paid"] == starting_paid

        # Record a payment + transaction timestamp
        r = client.patch(
            f"/clients/{target.id}",
            json={
                "amount_paid": starting_paid + 5000.0,
                "latest_transaction_date": "2026-05-16T10:00:00",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["amount_paid"] == starting_paid + 5000.0
        assert body["latest_transaction_date"] == "2026-05-16T10:00:00"
        # Earlier billing update is preserved
        assert body["billed_amount"] == new_billed
