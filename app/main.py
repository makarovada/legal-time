from fastapi import FastAPI, Depends, HTTPException
from app.routers import auth, client, contract, matter, time_entry, employee
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.utils.auth import get_current_user
from app.utils.google_calendar import get_google_oauth_flow, encrypt_token
import json


app = FastAPI(title="LegalTime", version="0.1.0")
app.include_router(auth.router)
app.include_router(client.router)
app.include_router(contract.router)
app.include_router(matter.router)
app.include_router(time_entry.router)
app.include_router(employee.router)

# Дополнительный эндпоинт для Google callback без префикса /auth
# (для совместимости с redirect URI в Google Cloud Console)
@app.get("/google/callback")
def google_callback_no_prefix(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Обработка callback от Google OAuth (без префикса /auth)"""
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
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/google/callback"
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

@app.get("/")
def root():
    return {"message": "LegalTime API is running!"}

@app.get("/debug-config")
def debug_config():
   return {
       "database_url": settings.DATABASE_URL,
       "google_client_id": settings.GOOGLE_CLIENT_ID,
       "fernet_key_set": settings.FERNET_KEY is not None
   }