from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Matter(BaseModel):
    __tablename__ = "matters"

    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    contract = relationship("Contract", back_populates="matters")
    time_entries = relationship("TimeEntry", back_populates="matter")