from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # позволяет создавать из ORM объектов