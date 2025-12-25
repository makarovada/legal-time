from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ClientType(str, enum.Enum):
    legal = "legal"
    physical = "physical"

class Client(BaseModel):
    __tablename__ = "clients"

    name = Column(String, nullable=False, index=True)
    type = Column(Enum(ClientType), nullable=False)
    contracts = relationship("Contract", back_populates="client")