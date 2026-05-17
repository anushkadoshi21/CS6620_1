from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    name: str
    organization_type: str
    total_headcount: int = Field(ge=0)
    joined_at: datetime
    total_valuation: float = Field(ge=0)
    billed_amount: float = Field(ge=0)
    amount_paid: float = Field(ge=0)
    latest_transaction_date: Optional[datetime] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    organization_type: Optional[str] = None
    total_headcount: Optional[int] = Field(default=None, ge=0)
    joined_at: Optional[datetime] = None
    total_valuation: Optional[float] = Field(default=None, ge=0)
    billed_amount: Optional[float] = Field(default=None, ge=0)
    amount_paid: Optional[float] = Field(default=None, ge=0)
    latest_transaction_date: Optional[datetime] = None


class ClientResponse(ClientBase):
    id: UUID = Field(default_factory=uuid4)
