import os
from typing import List, Optional
from app.models.client import ClientCreate, ClientResponse, ClientUpdate
import boto3
from botocore.exceptions import ClientError
    
TABLE_NAME = "clients"
BUCKET_NAME = "clients"
ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_REGION", "us-east-1")


class ClientService:

    def _dynamo(self):
        return boto3.resource(
            "dynamodb",
            endpoint_url=ENDPOINT_URL,
            region_name=REGION,
            aws_access_key_id="test",
        aws_secret_access_key="test",
    ).Table(TABLE_NAME)


    def _s3(self):
        return boto3.client(
            "s3",
            endpoint_url=ENDPOINT_URL,
            region_name=REGION,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    @classmethod
    def list_clients(cls) -> List[ClientResponse]:
        try:
            response = self._dynamo().scan()
            items = response.get("Items", [])
            return [ClientResponse(**item) for item in items]
        except ClientError as e:
            print(f"Error listing clients: {e}")
            return []

    @classmethod
    def get_client(cls, client_name: str) -> Optional[ClientResponse]:
        try:
            response = self._dynamo().get_item(Key={"name": client_name})
            item = response.get("Item")
            return ClientResponse(**item) if item else None
        except ClientError as e:
            print(f"Error getting client: {e}")
            return None

    @classmethod
    def create_client(cls, payload: ClientCreate) -> ClientResponse:
        client = ClientResponse(**payload.model_dump())
        try:
            self._dynamo().put_item(Item=client.model_dump())
            return client
        except ClientError as e:
            print(f"Error creating client: {e}")
            raise

    @classmethod
    def update_client(
        cls, client_name: str, payload: ClientUpdate
    ) -> Optional[ClientResponse]:
        try:
            existing = cls.get_client(client_name)
            if existing is None:
                return None
            updated = existing.model_copy(
                update=payload.model_dump(exclude_unset=True)
            )
            self._dynamo().put_item(Item=updated.model_dump())
            return updated
        except ClientError as e:
            print(f"Error updating client: {e}")
            raise

    @classmethod
    def delete_client(cls, client_name: str) -> bool:
        try:
            response = self._dynamo().delete_item(
                Key={"name": client_name}, ReturnValues="ALL_OLD"
            )
            return "Attributes" in response
        except ClientError as e:
            print(f"Error deleting client: {e}")
            return False
