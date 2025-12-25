from .base import BaseSchema
from typing import Optional

class EmployeeBase(BaseSchema):
    name: str
    email: str
    role: str  # "lawyer", "senior_lawyer", "admin"

class EmployeeCreate(EmployeeBase):
    password: str

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True