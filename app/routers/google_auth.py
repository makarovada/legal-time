from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cryptography.fernet import Fernet
from datetime import datetime
from app.database import get_db
from app.models.google_token import UserGoogleToken
from app.models.employee import Employee
from app.utils.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/google", tags=["google"])

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def get_flow(redirect_uri: str = settings.GOOGLE_REDIRECT_URI):
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

@router.get("/auth")
def google_auth(current_user: Employee = Depends(get_current_user)):
    flow = get_flow()
    authorization_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    return RedirectResponse(authorization_url)

@router.get("/callback")
def google_callback(request: Request, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    flow = get_flow(str(request.url))
    try:
        flow.fetch_token(authorization_response=str(request.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {str(e)}")

    credentials = flow.credentials
    if not credentials.token:
        raise HTTPException(status_code=400, detail="Access token не получен")

    fernet = Fernet(settings.FERNET_KEY.encode())
    encrypted_access = fernet.encrypt(credentials.token.encode()).decode()
    encrypted_refresh = fernet.encrypt(credentials.refresh_token.encode()).decode() if credentials.refresh_token else None
    expires_at = credentials.expiry if credentials.expiry else None

    # Проверяем существующий токен
    existing_token = db.query(UserGoogleToken).filter(UserGoogleToken.employee_id == current_user.id).first()
    if existing_token:
        existing_token.access_token = encrypted_access
        existing_token.refresh_token = encrypted_refresh
        existing_token.expires_at = expires_at
    else:
        new_token = UserGoogleToken(
            employee_id=current_user.id,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            expires_at=expires_at
        )
        db.add(new_token)
    db.commit()

    return RedirectResponse("/dashboard")  # Или куда-то в профиль

def get_google_service(db: Session, user_id: int):
    token = db.query(UserGoogleToken).filter(UserGoogleToken.employee_id == user_id).first()
    if not token:
        raise HTTPException(status_code=400, detail="Google Calendar не подключён")

    fernet = Fernet(settings.FERNET_KEY.encode())
    access_token = fernet.decrypt(token.access_token.encode()).decode()
    refresh_token = fernet.decrypt(token.refresh_token.encode()).decode() if token.refresh_token else None

    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )

    # Авто-refresh если expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return build("calendar", "v3", credentials=credentials)

@router.get("/import-events")
def import_events(date: str, current_user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    service = get_google_service(db, current_user.id)
    try:
        start_time = datetime.fromisoformat(date).isoformat() + "Z"
        end_time = (datetime.fromisoformat(date) + timedelta(days=1)).isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        # Здесь логика предзаполнения таймшита: парсинг summary, duration и т.д.
        # Для примера возвращаем сырые события
        return {"events": events}
    except HttpError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Аналогично добавьте endpoints для создания событий, reminders (по ТЗ)
# Например, @router.post("/create-event") с body для Matter creation