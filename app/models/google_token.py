from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.models.base import BaseModel
from datetime import datetime

class UserGoogleToken(BaseModel):
    __tablename__ = "user_google_tokens"

    user_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Опционально: зашифруем токены позже через Fernet