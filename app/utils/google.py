from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from app.config import settings
from app.models.google_token import UserGoogleToken
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def get_google_credentials(db: Session, user_id: int):
    token = db.query(UserGoogleToken).filter(UserGoogleToken.user_id == user_id).first()
    if not token:
        return None

    credentials = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token.access_token = credentials.token
        token.expires_at = datetime.fromtimestamp(credentials.expiry.timestamp())
        db.commit()

    return credentials