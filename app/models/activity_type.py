from sqlalchemy import Column, String
from .base import BaseModel

class ActivityType(BaseModel):
    __tablename__ = "activity_types"

    name = Column(String, unique=True, nullable=False)