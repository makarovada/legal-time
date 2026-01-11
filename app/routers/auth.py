from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi import Body
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.models.employee import Employee
from app.schemas.auth import Token
from datetime import timedelta
from app.config import settings
from fastapi.security import OAuth2PasswordRequestFormStrict  # <-- новый импорт
from app.utils.google_calendar import get_google_oauth_flow, encrypt_token
import json


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestFormStrict = Depends(),  # <-- Strict версия
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Для создания первого админа (одноразово)
@router.post("/create-admin")
def create_admin(email: str = Body(..., embed=True), password: str = Body(..., embed=True), db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.role == "admin").first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    hashed = get_password_hash(password)
    admin = Employee(email=email, password_hash=hashed, name="Admin", role="admin")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"message": "Admin created"}


# Google Calendar OAuth интеграция
@router.get("/google/authorize")
def google_authorize(
    request: Request,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Начать процесс авторизации Google Calendar"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth credentials not configured"
        )
    
    # Формируем redirect URI
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{base_url}/auth/google/callback"
    
    flow = get_google_oauth_flow(redirect_uri)
    
    # Сохраняем user_id в state для безопасности
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=str(current_user.id)  # Сохраняем ID пользователя в state
    )
    
    return {"authorization_url": authorization_url, "state": state}


@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Обработка callback от Google OAuth"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    # Получаем пользователя из state
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    user = db.query(Employee).filter(Employee.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth credentials not configured"
        )
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/auth/google/callback"
    flow = get_google_oauth_flow(redirect_uri)
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Сохраняем токены в зашифрованном виде
        token_data = {
            'token': credentials.token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        user.google_token_encrypted = encrypt_token(json.dumps(token_data))
        if credentials.refresh_token:
            user.google_refresh_token_encrypted = encrypt_token(credentials.refresh_token)
        
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Google Calendar successfully connected",
            "calendar_id": user.google_calendar_id or "primary"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange authorization code: {str(e)}")


@router.post("/google/disconnect")
def google_disconnect(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отключить интеграцию с Google Calendar"""
    current_user.google_token_encrypted = None
    current_user.google_refresh_token_encrypted = None
    current_user.google_calendar_id = None
    db.commit()
    
    return {"message": "Google Calendar disconnected successfully"}


@router.get("/google/status")
def google_status(
    current_user: Employee = Depends(get_current_user)
):
    """Проверить статус интеграции с Google Calendar"""
    is_connected = current_user.google_token_encrypted is not None
    return {
        "connected": is_connected,
        "calendar_id": current_user.google_calendar_id if is_connected else None
    }