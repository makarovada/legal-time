from .base import BaseSchema

class ActivityTypeBase(BaseSchema):
    name: str

class ActivityTypeCreate(ActivityTypeBase):
    pass

class ActivityType(ActivityTypeBase):
    id: int

    class Config:
        from_attributes = True


