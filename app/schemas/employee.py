from .base import BaseSchema
from typing import Optional

class EmployeeBase(BaseSchema):
    name: str
    email: str
    role: str  # "lawyer", "senior_lawyer", "admin"

class EmployeeCreate(EmployeeBase):
    password: Optional[str] = None  # Пароль опционален при обновлении

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True