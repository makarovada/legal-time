import os
from pathlib import Path
from pydantic_settings import BaseSettings

# 1. Определяем, где лежит этот файл (config.py)
# .parent -> папка app
# .parent.parent -> папка проекта (legal-time)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Собираем полный путь к .env
ENV_FILE_PATH = BASE_DIR / ".env"

# # ДЛЯ ОТЛАДКИ (можешь удалить потом):
# print(f"Ищем .env здесь: {ENV_FILE_PATH}")
# print(f"Файл существует? {ENV_FILE_PATH.exists()}")

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Optional поля...
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/google/callback"
    FERNET_KEY: str 
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    class Config:
        # 3. Передаем абсолютный путь (преобразуем в строку)
        env_file = str(ENV_FILE_PATH)
        env_file_encoding = "utf-8"
        # Важно: если файла нет, не игнорировать ошибку (чтобы мы поняли сразу)
        extra = "ignore" 

settings = Settings()