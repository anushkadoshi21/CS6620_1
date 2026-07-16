import os
from typing import List, Optional
import json
from decimal import Decimal
from fastapi import HTTPException
from app.models.client import ClientCreate, ClientResponse, ClientUpdate
import boto3
from botocore.exceptions import ClientError
    
TABLE_NAME = "clients"
BUCKET_NAME = "clients"
ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.getenv("AWS_REGION", "us-east-1")

#Exceptions for service layer
class DuplicateClientError(Exception): pass
class ClientNotFoundError(Exception): pass
class InternalError(Exception): pass

class ClientService:
    @classmethod
    def convert_to_decimal(cls, item: dict) -> dict:
        # DynamoDB refuses Python floats; round-trip through JSON with Decimal parser.
        return json.loads(json.dumps(item), parse_float=Decimal)

    @classmethod
    def _dynamo(cls):
        return boto3.resource(
            "dynamodb",
            endpoint_url=ENDPOINT_URL,
            region_name=REGION,
            aws_access_key_id="test",
        aws_secret_access_key="test",
    ).Table(TABLE_NAME)

    @classmethod
    def _s3(cls):
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
            response = cls._dynamo().scan()
            items = response.get("Items", [])
            return [ClientResponse(**item) for item in items]
        except ClientError as e:
            print(f"Error listing clients: {e}")
            raise InternalError("Internal server error")

    @classmethod
    def get_client(cls, client_name: str) -> Optional[ClientResponse]:
        try:
            response = cls._dynamo().get_item(Key={"name": client_name})
            item = response.get("Item")
            return ClientResponse(**item)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ClientNotFoundError("Client not found")
            print(f"Error getting client: {e}")
            raise InternalError("Internal server error")

    @classmethod
    def create_client(cls, payload: ClientCreate) -> ClientResponse:
        client = ClientResponse(**payload.model_dump())
        try:
            cls._dynamo().put_item(
                Item=cls.convert_to_decimal(client.model_dump()),
                ConditionExpression="attribute_not_exists(#n)",
                ExpressionAttributeNames={"#n": "name"},
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise DuplicateClientError("Client already exists")
            else:
                print(f"Error creating client: {e}")
                raise InternalError("Internal server error")
        # DynamoDB write succeeded. Now S3.
        try:
            cls._s3().put_object(
                Bucket=BUCKET_NAME,
                Key=client.name,
                Body=client.model_dump_json().encode("utf-8"),
                ContentType="application/json",
            )
        except ClientError as e:
            print(f"Error writing to S3: {e}")
            # Rollback DynamoDB write
            cls._dynamo().delete_item(Key={"name": client.name})
            raise InternalError("Internal server error")
        return client

    @classmethod
    def update_client(
        cls, client_name: str, payload: ClientUpdate
    ) -> Optional[ClientResponse]:
        try:
            existing = cls.get_client(client_name)
            if existing is None:
                return None
            updated=cls._dynamo().put_item(Item=cls.convert_to_decimal( **payload.model_dump()))
            return updated
        except ClientError as e:
            print(f"Error updating client: {e}")
            raise InternalError("Internal server error")

    @classmethod
    def delete_client(cls, client_name: str) -> bool:
        try:
            response = cls._dynamo().delete_item(
                Key={"name": name},
                ConditionExpression="attribute_exists(#n)",
                ExpressionAttributeNames={"#n": "name"},
                ReturnValues="ALL_OLD",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ClientNotFoundError("Client not found")
            raise InternalError("Internal server error")

        old_item = response["Attributes"]

        try:
            cls._s3().delete_object(Bucket=BUCKET_NAME, Key=client_name)
        except ClientError as e:
            # Rollback: re-insert the DynamoDB item so stores stay consistent.
            cls._dynamo().put_item(Item=old_item)
            raise InternalError("Internal server error")
                    
