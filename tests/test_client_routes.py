from uuid import uuid4

from app.constants import DUMMY_CLIENTS


class TestListClients:
    def test_returns_seeded(self, client):
        r = client.get("/clients")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == len(DUMMY_CLIENTS)
        assert {c["id"] for c in body} == {str(c.id) for c in DUMMY_CLIENTS}


class TestGetClient:
    def test_found(self, client):
        target = DUMMY_CLIENTS[0]
        r = client.get(f"/clients/{target.id}")
        assert r.status_code == 200
        assert r.json()["name"] == target.name

    def test_not_found(self, client):
        r = client.get(f"/clients/{uuid4()}")
        assert r.status_code == 404
        assert r.json()["detail"] == "Client not found"

    def test_invalid_uuid(self, client):
        r = client.get("/clients/not-a-uuid")
        assert r.status_code == 422


class TestCreateClient:
    def test_creates(self, client, sample_client_payload):
        r = client.post("/clients", json=sample_client_payload)
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == sample_client_payload["name"]
        assert "id" in body

        follow_up = client.get(f"/clients/{body['id']}")
        assert follow_up.status_code == 200

    def test_missing_required_field(self, client, sample_client_payload):
        sample_client_payload.pop("name")
        r = client.post("/clients", json=sample_client_payload)
        assert r.status_code == 422

    def test_negative_headcount_rejected(self, client, sample_client_payload):
        sample_client_payload["total_headcount"] = -5
        r = client.post("/clients", json=sample_client_payload)
        assert r.status_code == 422


class TestUpdateClient:
    def test_partial_update(self, client):
        target = DUMMY_CLIENTS[0]
        r = client.patch(
            f"/clients/{target.id}",
            json={"name": "Renamed Co", "total_headcount": 999},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Renamed Co"
        assert body["total_headcount"] == 999
        assert body["organization_type"] == target.organization_type

    def test_not_found(self, client):
        r = client.patch(f"/clients/{uuid4()}", json={"name": "x"})
        assert r.status_code == 404

    def test_negative_value_rejected(self, client):
        target = DUMMY_CLIENTS[0]
        r = client.patch(
            f"/clients/{target.id}", json={"amount_paid": -1.0}
        )
        assert r.status_code == 422


class TestDeleteClient:
    def test_deletes(self, client):
        target = DUMMY_CLIENTS[0]
        r = client.delete(f"/clients/{target.id}")
        assert r.status_code == 204

        follow_up = client.get(f"/clients/{target.id}")
        assert follow_up.status_code == 404

    def test_not_found(self, client):
        r = client.delete(f"/clients/{uuid4()}")
        assert r.status_code == 404
