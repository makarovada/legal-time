from .base import BaseSchema
from typing import Optional
from datetime import date

class ContractBase(BaseSchema):
    number: str
    date: date
    client_id: int

class ContractCreate(ContractBase):
    pass

class Contract(ContractBase):
    id: int

    class Config:
        from_attributes = True