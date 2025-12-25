from app.crud.base import CRUDBase
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import TimeEntryCreate

class CRUDTimeEntry(CRUDBase[TimeEntry]):
    pass

time_entry = CRUDTimeEntry(TimeEntry)