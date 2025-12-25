from sqlalchemy import Column, Integer, Float, String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class TimeEntryStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"

class TimeEntry(BaseModel):
    __tablename__ = "time_entries"

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    rate_id = Column(Integer, ForeignKey("rates.id"), nullable=True)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), nullable=False)
    
    hours = Column(Float, nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    status = Column(Enum(TimeEntryStatus), default=TimeEntryStatus.draft)

    # Строковая ссылка
    employee = relationship("Employee", back_populates="time_entries")
    matter = relationship("Matter", back_populates="time_entries")