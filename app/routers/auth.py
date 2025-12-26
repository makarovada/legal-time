from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm   # ← меняем здесь
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.models.client import Client
from app.utils.auth import authenticate_user, create_access_token
from app.config import settings
from datetime import timedelta
from app.common import templates

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_class=HTMLResponse)
def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный email или пароль"
        })

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    # Устанавливаем HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600 * 24,  # 24 часа
        expires=3600 * 24,
        secure=False,  # для localhost
        samesite="lax"
    )

    clients = db.query(Client).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": user,
        "clients": clients
    })

@router.get("/logout", response_class=HTMLResponse, name="logout")
def logout(response: Response, request: Request):
    response.delete_cookie(key="access_token")
    return templates.TemplateResponse("login.html", {"request": request})