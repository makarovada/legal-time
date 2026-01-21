from typing import Optional
from datetime import date

from .base import BaseSchema
from .rate import Rate as RateSchema


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
    status: str = "draft"  # draft / approved
    rate: Optional[RateSchema] = None
    rate_value: Optional[float] = None

    class Config:
        from_attributes = True