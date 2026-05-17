from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=List[ClientResponse])
def list_clients():
    return ClientService.list_clients()


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate):
    return ClientService.create_client(payload)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: UUID):
    client = ClientService.get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(client_id: UUID, payload: ClientUpdate):
    client = ClientService.update_client(client_id, payload)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: UUID):
    if not ClientService.delete_client(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return None
