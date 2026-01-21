from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import time
from app.routers import auth, client, contract, matter, time_entry, employee, activity_type, rate
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.utils.auth import get_current_user
from app.utils.google_calendar import get_google_oauth_flow, encrypt_token
import json

# Определяем путь к статическим файлам
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - выводим все зарегистрированные роуты
    print("\n=== Registered Routes ===")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"{methods:10} {route.path}")
    print("========================\n")
    yield
    # Shutdown

app = FastAPI(
    title="LegalTime", 
    version="0.1.0", 
    lifespan=lifespan,
    redirect_slashes=True  # Автоматически перенаправлять с /path на /path/ и наоборот
)

# Middleware для логирования всех запросов
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        print(f"📥 {request.method} {request.url.path}?{request.url.query}")
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"📤 {response.status_code} {request.method} {request.url.path} ({process_time:.3f}s)")
        return response

app.add_middleware(LoggingMiddleware)

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роутеры
# Auth роутер подключаем дважды:
# 1. Без префикса /api для Swagger и OAuth2 стандарта (auth/login)
app.include_router(auth.router)
# 2. С префиксом /api для фронтенда (/api/auth/login)
app.include_router(auth.router, prefix="/api")
# Остальные роутеры только с префиксом /api
app.include_router(client.router, prefix="/api")
app.include_router(contract.router, prefix="/api")
app.include_router(matter.router, prefix="/api")
app.include_router(time_entry.router, prefix="/api")
app.include_router(employee.router, prefix="/api")
app.include_router(rate.router, prefix="/api")
app.include_router(activity_type.router, prefix="/api")

# Статические файлы (CSS, JS, изображения)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

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
        
        # Создаем отдельный календарь LegalTime, если его еще нет
        if not user.google_calendar_id:
            from app.utils.google_calendar import create_legal_time_calendar
            calendar_id = create_legal_time_calendar(user)
            if calendar_id:
                user.google_calendar_id = calendar_id
        
        db.commit()
        db.refresh(user)
        
        calendar_id = user.google_calendar_id or "primary"
        # URL для открытия конкретного календаря в Google Calendar
        if calendar_id == "primary":
            calendar_url = "https://calendar.google.com/calendar/r"
        else:
            # Для отдельного календаря используем формат с email или ID
            calendar_url = f"https://calendar.google.com/calendar/r?cid={calendar_id}"
        
        # Возвращаем красивую HTML страницу в стиле Jira
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Calendar подключен - LegalTime</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #F4F5F7;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            border: 1px solid #DFE1E6;
            padding: 48px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }}
        .success-icon {{
            width: 64px;
            height: 64px;
            background: #0052CC;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
        }}
        .checkmark {{
            width: 32px;
            height: 32px;
            stroke: white;
            stroke-width: 3;
            stroke-linecap: round;
            stroke-linejoin: round;
            fill: none;
        }}
        h1 {{
            color: #42526E;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        p {{
            color: #42526E;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 32px;
        }}
        .buttons {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .btn {{
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .btn-primary {{
            background: #0052CC;
            color: white;
        }}
        .btn-primary:hover {{
            background: #0065FF;
        }}
        .btn-secondary {{
            background: #F4F5F7;
            color: #42526E;
            border: 1px solid #DFE1E6;
        }}
        .btn-secondary:hover {{
            background: #EBECF0;
        }}
        .info-box {{
            background: #F4F5F7;
            border: 1px solid #DFE1E6;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 24px;
            text-align: left;
        }}
        .info-box p {{
            margin: 0;
            font-size: 13px;
            color: #42526E;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">
            <svg class="checkmark" viewBox="0 0 24 24">
                <path d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h1>Google Calendar подключен!</h1>
        <p>
            Ваш Google Calendar успешно подключен к LegalTime.
        </p>
        <div class="info-box">
            <p><strong>✓</strong> Создан отдельный календарь "LegalTime" для ваших записей времени</p>
            <p style="margin-top: 8px;"><strong>✓</strong> Все новые записи времени будут автоматически синхронизироваться</p>
        </div>
        <div class="buttons">
            <a href="/dashboard" class="btn btn-primary">
                Перейти в дашборд
            </a>
            <a href="{calendar_url}" target="_blank" class="btn btn-secondary">
                Открыть Google Calendar
            </a>
        </div>
    </div>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        # Возвращаем страницу с ошибкой в том же стиле
        error_html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ошибка подключения - LegalTime</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #F4F5F7;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            border: 1px solid #DFE1E6;
            padding: 48px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }}
        .error-icon {{
            width: 64px;
            height: 64px;
            background: #DE350B;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 32px;
            color: white;
        }}
        h1 {{
            color: #42526E;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        p {{
            color: #42526E;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .error-detail {{
            background: #FFEBE6;
            border: 1px solid #FF5630;
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 24px;
            color: #BF2600;
            font-size: 13px;
            text-align: left;
        }}
        .btn {{
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            background: #0052CC;
            color: white;
            display: inline-block;
            transition: all 0.2s ease;
        }}
        .btn:hover {{
            background: #0065FF;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">✕</div>
        <h1>Ошибка подключения</h1>
        <p>Не удалось подключить Google Calendar.</p>
        <div class="error-detail">
            {str(e)}
        </div>
        <a href="/dashboard" class="btn">Вернуться в дашборд</a>
    </div>
</body>
</html>
        """
        return HTMLResponse(content=error_html, status_code=400)


# Serve React app for root and all non-API routes
# ВАЖНО: Эти роуты должны быть ПОСЛЕ всех API роутеров
@app.get("/")
def serve_root():
    """Serve React app index.html for root path"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {"message": "LegalTime API is running! Frontend not built yet. Run 'cd frontend && npm run build'"}

# Catch-all роут для SPA - должен быть последним
# ВАЖНО: В FastAPI более специфичные роуты обрабатываются первыми
# НО: этот роут НЕ должен обрабатывать API запросы
# Проблема: catch-all с {path:path} может перехватывать запросы до API роутеров
# Решение: проверяем начало пути и перенаправляем API запросы на версию со слэшем
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def serve_frontend(request: Request, full_path: str):
    """
    Serve React app for SPA routing.
    Этот роут обрабатывает только пути для фронтенда (не API).
    """
    # КРИТИЧНО: Если путь начинается с api/, НЕ обрабатываем его здесь
    # FastAPI должен был обработать его в API роутерах выше
    # Если мы здесь, значит либо роут не найден, либо проблема с завершающим слэшем
    if full_path.startswith("api/"):
        # Проблема: роуты зарегистрированы с завершающим слэшем (/api/time-entries/)
        # но запросы идут без него (/api/time-entries)
        # Решение: перенаправляем на версию с завершающим слэшем
        from fastapi.responses import RedirectResponse
        path_with_slash = f"/{full_path}/" if not full_path.endswith("/") else f"/{full_path}"
        query_string = f"?{request.url.query}" if request.url.query else ""
        print(f"🔄 Redirecting API request: {request.method} /{full_path} → {path_with_slash}{query_string}")
        # 307 Temporary Redirect сохраняет метод запроса (GET, POST, и т.д.)
        return RedirectResponse(url=path_with_slash + query_string, status_code=307)
    
    # Для всех остальных путей возвращаем index.html (SPA routing) - только для GET
    if request.method == "GET":
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return {"message": "LegalTime API is running! Frontend not built yet. Run 'cd frontend && npm run build'"}
    else:
        # Для не-GET запросов к не-API путям возвращаем 404
        raise HTTPException(status_code=404, detail=f"Endpoint not found: {request.method} /{full_path}")

@app.get("/debug-config")
def debug_config():
   return {
       "database_url": settings.DATABASE_URL,
       "google_client_id": settings.GOOGLE_CLIENT_ID,
       "fernet_key_set": settings.FERNET_KEY is not None
   }