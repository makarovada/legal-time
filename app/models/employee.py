from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class EmployeeRole(str, enum.Enum):
    lawyer = "lawyer"
    senior_lawyer = "senior_lawyer"
    admin = "admin"

class Employee(BaseModel):
    __tablename__ = "employees"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(EmployeeRole), nullable=False, default=EmployeeRole.lawyer)

    time_entries = relationship("TimeEntry", back_populates="employee")