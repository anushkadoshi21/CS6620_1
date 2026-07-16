from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.client_service import ClientService, DuplicateClientError, ClientNotFoundError, InternalError


router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=List[ClientResponse],status_code=status.HTTP_200_OK)
def list_clients():
    try:
        return ClientService.list_clients()
    except InternalError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_name}", response_model=ClientResponse, status_code=status.HTTP_200_OK)
def get_client(client_name: str): #incorrect parameter type will result in status 422 error
    try:
        client = ClientService.get_client(client_name)
    except ClientNotFoundError:
        raise HTTPException(status_code=404, detail="Client not found")
    except InternalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return client

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate):
    try:
        new_client = ClientService.create_client(payload)
    except DuplicateClientError:
        raise HTTPException(status_code=409, detail="Client already exists")
    except InternalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return new_client

@router.put("/{client_name}", response_model=ClientResponse, status_code=status.HTTP_200_OK)
def update_client(client_name: str, payload: ClientUpdate):
    try:
        client = ClientService.update_client(client_name, payload)
    except ClientNotFoundError:
        raise HTTPException(status_code=404, detail="Client not found")
    except InternalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return client


@router.delete("/{client_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_name: str):
    try:
        ClientService.delete_client(client_name)
    except ClientNotFoundError:
        raise HTTPException(status_code=404, detail="Client not found")
    except InternalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"detail": "Client deleted successfully"}
