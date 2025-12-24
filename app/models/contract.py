from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Contract(BaseModel):
    __tablename__ = "contracts"

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    number = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)

    client = relationship("Client", back_populates="contracts")
    matters = relationship("Matter", back_populates="contract", cascade="all, delete-orphan")