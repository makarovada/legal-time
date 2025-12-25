from app.crud.base import CRUDBase
from app.models.contract import Contract
from app.schemas.contract import ContractCreate

class CRUDContract(CRUDBase[Contract]):
    pass

contract = CRUDContract(Contract)