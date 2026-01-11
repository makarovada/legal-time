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
    
    # Google Calendar интеграция
    google_token_encrypted = Column(String, nullable=True)
    google_refresh_token_encrypted = Column(String, nullable=True)
    google_calendar_id = Column(String, nullable=True)  # ID календаря для синхронизации

    # Строковая ссылка — SQLAlchemy найдёт класс позже
    time_entries = relationship("TimeEntry", back_populates="employee")