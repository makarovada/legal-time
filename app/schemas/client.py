from .base import BaseSchema
from typing import Optional

class ClientBase(BaseSchema):
    name: str
    type: str  # "legal" or "physical"

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        from_attributes = True