from typing import Optional

from .base import BaseSchema


class RateBase(BaseSchema):
    value: float
    employee_id: Optional[int] = None
    contract_id: Optional[int] = None


class RateCreate(RateBase):
    pass


class Rate(RateBase):
    id: int

    class Config:
        from_attributes = True


