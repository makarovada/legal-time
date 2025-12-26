from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models.employee import Employee
from app.schemas.auth import TokenData
from app.config import settings

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Хэширование пароля
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Аутентификация пользователя (по email и паролю)
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(Employee).filter(Employee.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

# Создание JWT-токена
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Получение текущего пользователя из cookie
def get_current_user(
    access_token: str | None = Cookie(default=None, alias="access_token"),
    db: Session = Depends(get_db)
):
    if access_token is None:
        raise credentials_exception

    # Убираем "Bearer " если есть
    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Employee).filter(Employee.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Только админ
def get_current_admin_user(current_user: Employee = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user