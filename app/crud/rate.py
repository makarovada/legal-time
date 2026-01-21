from app.crud.base import CRUDBase
from app.models.rate import Rate as RateModel


class CRUDRate(CRUDBase[RateModel]):
    pass


rate = CRUDRate(RateModel)


