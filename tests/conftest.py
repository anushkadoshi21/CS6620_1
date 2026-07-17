import os
import boto3
import httpx
import pytest


API_URL = os.getenv("API_URL", "http://localhost:8000")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
TABLE_NAME = "clients"
BUCKET_NAME = "clients"


# Session-scoped clients (built once, reused)

@pytest.fixture(scope="session")
def api():
    with httpx.Client(base_url=API_URL, timeout=10.0) as client:
        yield client


@pytest.fixture(scope="session")
def dynamo():
    return boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ).Table(TABLE_NAME)


@pytest.fixture(scope="session")
def s3():
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


# Sample payloads 

@pytest.fixture
def sample_client():
    return {
        "name": "test-client",
        "organization_type": "startup",
        "total_headcount": 50,
        "total_valuation": 1000000.0,
        "billed_amount": 5000.0,
        "amount_paid": 5000.0,
    }


@pytest.fixture
def updated_client(sample_client):
    return {
        **sample_client,
        "total_headcount": 75,
        "amount_paid": 6000.0,
    }


#  State-management fixtures 

def _wipe(dynamo, s3):
    """Delete every item from DynamoDB and every object from S3."""
    scan = dynamo.scan()
    with dynamo.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"name": item["name"]})

    objs = s3.list_objects_v2(Bucket=BUCKET_NAME).get("Contents", [])
    for obj in objs:
        s3.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])


@pytest.fixture
def clean_state(dynamo, s3):
    """Wipe both stores before and after the test."""
    _wipe(dynamo, s3)
    yield
    _wipe(dynamo, s3)


@pytest.fixture
def seeded_client(api, dynamo, s3, sample_client):
    """Wipe both stores, POST a sample client, yield the payload, clean up after."""
    _wipe(dynamo, s3)
    response = api.post("/clients", json=sample_client)
    assert response.status_code == 201, (
        f"Seed failed: {response.status_code} {response.text}"
    )
    yield sample_client
    _wipe(dynamo, s3)