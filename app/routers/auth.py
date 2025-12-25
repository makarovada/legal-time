from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import authenticate_user, create_access_token, get_password_hash
from app.models.employee import Employee
from app.schemas.auth import Token
from datetime import timedelta
from app.config import settings
from fastapi.security import OAuth2PasswordRequestFormStrict  # <-- новый импорт


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