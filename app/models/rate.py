from sqlalchemy import Column, Integer, Float, ForeignKey
from .base import BaseModel

class Rate(BaseModel):
    __tablename__ = "rates"

    value = Column(Float, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)