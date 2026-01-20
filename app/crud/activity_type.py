from app.crud.base import CRUDBase
from app.models.activity_type import ActivityType as ActivityTypeModel
from app.schemas.activity_type import ActivityTypeCreate, ActivityType

class CRUDActivityType(CRUDBase[ActivityTypeModel]):
    pass

activity_type = CRUDActivityType(ActivityTypeModel)

