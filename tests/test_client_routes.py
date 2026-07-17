
import json
from decimal import Decimal

import pytest
from botocore.exceptions import ClientError


BUCKET_NAME = "clients"

#Helper functions 

def _normalize(item):
    """Convert Decimals from DynamoDB back to native numeric types."""
    if item is None:
        return None
    op = {}
    for k, v in item.items():
        if isinstance(v, Decimal):
            op[k] = int(v) if v % 1 == 0 else float(v)
        else:
            op[k] = v
    return op 

def _assert_s3_dynamo_match(dynamo, s3, name):
    dynamo_item = _normalize(dynamo.get_item(Key={"name": name}).get("Item"))
    assert dynamo_item is not None, f"DynamoDB missing item '{name}'"

    s3_body = s3.get_object(Bucket=BUCKET_NAME, Key=name)["Body"].read()
    s3_item = json.loads(s3_body)

    assert dynamo_item == s3_item, (
        f"Stores diverged for '{name}':\n"
        f"  DynamoDB: {dynamo_item}\n"
        f"  S3:       {s3_item}"
    )

def _assert_neither_s3_dynamo_has(dynamo, s3, name):
    dynamo_resp = dynamo.get_item(Key={"name": name})
    assert "Item" not in dynamo_resp, f"DynamoDB still has '{name}'"

    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=name)
        pytest.fail(f"S3 still has object '{name}'")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")




class TestListClients:
    def test_empty(self, api,clean_state):
        r = api.get("/clients")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_seeded(self, api, dynamo,s3, seeded_client):
        r = api.get("/clients")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 1
        assert body[0]["name"] == seeded_client["name"]
        _assert_s3_dynamo_match(dynamo, s3, seeded_client["name"])


class TestGetClient:
    def test_found_client(self, api, dynamo, s3, seeded_client):
        r = api.get(f"/clients/{seeded_client['name']}")
        assert r.status_code == 200
        assert r.json()["name"] == seeded_client["name"]
        _assert_s3_dynamo_match(dynamo, s3, seeded_client["name"])

    def test_not_found_client(self, api,dynamo,s3,clean_state):
        r = api.get(f"/clients/dummy-client")
        assert r.status_code == 404
        assert r.json()["detail"] == "Client not found"
        _assert_neither_s3_dynamo_has(dynamo, s3, "dummy-client")

    def test_invalid_parameters(self, api, dynamo, s3, clean_state): 
        """Test that invalid parameters (in this case num,bers arent allowed in client names) result in a 422 error."""
        r = api.get("/clients/123")
        assert r.status_code == 422
        _assert_neither_s3_dynamo_has(dynamo, s3, "123")


class TestCreateClient:
    def test_creates(self, api, dynamo, s3, clean_state, sample_client):
        r = api.post("/clients", json=sample_client)
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == sample_client["name"]
        _assert_s3_dynamo_match(dynamo, s3, sample_client["name"])

    def test_duplicate_rejected(self, api, dynamo, s3, seeded_client):
        r = api.post("/clients", json=seeded_client)
        assert r.status_code == 409
        assert r.json()["detail"] == "Client already exists"
        _assert_s3_dynamo_match(dynamo, s3, seeded_client["name"])

    def test_missing_required_field(self, api, dynamo, s3, clean_state, sample_client):
        sample_client.pop("organization_type")
        r = api.post("/clients", json=sample_client)
        assert r.status_code == 422
        _assert_neither_s3_dynamo_has(dynamo, s3, sample_client["name"])

    def test_negative_headcount_rejected(self, api, s3, dynamo, sample_client):
        sample_client["total_headcount"] = -5
        r = api.post("/clients", json=sample_client)
        assert r.status_code == 422
        _assert_neither_s3_dynamo_has(dynamo, s3, sample_client["name"])

    


class TestUpdateClient:
    def test_update(self, api, dynamo, s3, seeded_client):
        r = api.put(
            f"/clients/{seeded_client['name']}",
            json={**seeded_client, "total_headcount": 999},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == seeded_client["name"]
        assert body["total_headcount"] == 999
        _assert_s3_dynamo_match(dynamo, s3, seeded_client["name"])

    def test_not_found(self, api, dynamo, s3, clean_state):
        r = api.put(f"/clients/dummy-client", json={ "organization_type": "startup",
        "total_headcount": 50,
        "total_valuation": 1000000.0,
        "billed_amount": 5000.0,
        "amount_paid": 5000.0,})
        assert r.status_code == 404
        assert r.json()["detail"] == "Client not found"
        _assert_neither_s3_dynamo_has(dynamo, s3, "dummy-client")


class TestDeleteClient:
    def test_deletes(self, api, dynamo, s3, seeded_client):
        r = api.delete(f"/clients/{seeded_client['name']}")
        assert r.status_code == 204
        _assert_neither_s3_dynamo_has(dynamo, s3, seeded_client["name"])

    def test_not_found(self, api, dynamo, s3, clean_state):
        r = api.delete(f"/clients/dummy-client")
        assert r.status_code == 404
        _assert_neither_s3_dynamo_has(dynamo, s3, "dummy-client")
