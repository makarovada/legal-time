from app.crud.base import CRUDBase
from app.models.matter import Matter
from app.schemas.matter import MatterCreate

class CRUDMatter(CRUDBase[Matter]):
    pass

matter = CRUDMatter(Matter)