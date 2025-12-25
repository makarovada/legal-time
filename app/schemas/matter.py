from .base import BaseSchema
from typing import Optional

class MatterBase(BaseSchema):
    code: str
    name: str
    description: Optional[str] = None
    contract_id: int

class MatterCreate(MatterBase):
    pass

class Matter(MatterBase):
    id: int

    class Config:
        from_attributes = True