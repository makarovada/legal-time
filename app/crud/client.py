from app.crud.base import CRUDBase
from app.models.client import Client
from app.schemas.client import ClientCreate

class CRUDClient(CRUDBase[Client]):
    pass

client = CRUDClient(Client)