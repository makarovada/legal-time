from .base import BaseSchema
from typing import Optional
from datetime import date

class TimeEntryBase(BaseSchema):
    hours: float
    description: Optional[str] = None
    date: date
    matter_id: int
    activity_type_id: int
    rate_id: Optional[int] = None

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntry(TimeEntryBase):
    id: int
    employee_id: int
    status: str = "draft" # draft / approved

    class Config:
        from_attributes = True