from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.models.employee import Employee
from app.models.client import Client
from app.utils.auth import get_current_user

from app.routers import (
    auth,
    client,
    contract,
    matter,
    time_entry,
    employee,
    google_auth
)

app = FastAPI(
    title="LegalTime",
    description="Система учёта рабочего времени юристов",
    version="1.0.0",
    debug=True
)

# Статические файлы (если добавишь css/js)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="app/templates")

# Роутеры
app.include_router(auth.router)
app.include_router(client.router)
app.include_router(contract.router)
app.include_router(matter.router)
app.include_router(time_entry.router)
app.include_router(employee.router)
app.include_router(google_auth.router)

# Главная страница — логин
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Дашборд — после логина
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: Employee = Depends(get_current_user),
    db = Depends(get_db)
):
    clients = db.query(Client).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "current_user": current_user, "clients": clients}
    )

# Логаут
@app.post("/auth/logout")
def logout():
    response = RedirectResponse(url="/")
    # Если используешь cookies для токена — можно очистить
    return response

# Приветствие для корня API
@app.get("/api")
def api_root():
    return {"message": "LegalTime API работает! Документация: /docs"}