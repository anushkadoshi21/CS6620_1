from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    name: str
    organization_type: str
    total_headcount: int = Field(default=0, ge=0)
    total_valuation: float = Field(default=0, ge=0)
    billed_amount: float = Field(default=0, ge=0)
    amount_paid: float = Field(default=0, ge=0)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    organization_type: Optional[str] = None
    total_headcount: Optional[int] = Field(default=None, ge=0)
    total_valuation: Optional[float] = Field(default=None, ge=0)
    billed_amount: Optional[float] = Field(default=None, ge=0)
    amount_paid: Optional[float] = Field(default=None, ge=0)


class ClientResponse(ClientBase):
    pass
