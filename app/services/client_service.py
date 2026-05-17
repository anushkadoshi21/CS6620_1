from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.constants import DUMMY_CLIENTS
from app.models.client import ClientCreate, ClientResponse, ClientUpdate


class ClientService:
    _clients: Dict[UUID, ClientResponse] = {c.id: c for c in DUMMY_CLIENTS}

    @classmethod
    def list_clients(cls) -> List[ClientResponse]:
        return list(cls._clients.values())

    @classmethod
    def get_client(cls, client_id: UUID) -> Optional[ClientResponse]:
        return cls._clients.get(client_id)

    @classmethod
    def create_client(cls, payload: ClientCreate) -> ClientResponse:
        client = ClientResponse(id=uuid4(), **payload.model_dump())
        cls._clients[client.id] = client
        return client

    @classmethod
    def update_client(
        cls, client_id: UUID, payload: ClientUpdate
    ) -> Optional[ClientResponse]:
        existing = cls._clients.get(client_id)
        if existing is None:
            return None
        updated = existing.model_copy(
            update=payload.model_dump(exclude_unset=True)
        )
        cls._clients[client_id] = updated
        return updated

    @classmethod
    def delete_client(cls, client_id: UUID) -> bool:
        return cls._clients.pop(client_id, None) is not None
