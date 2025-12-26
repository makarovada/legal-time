from fastapi import FastAPI, Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.models.employee import Employee
from app.models.client import Client
from app.utils.auth import get_current_user
from app.common import templates

from app.routers import (
    auth,
    client,
    contract,
    matter,
    time_entry,
    employee,
    google_auth
)
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client, Matter, TimeEntry, Employee  # добавь нужные модели

app = FastAPI(
    title="LegalTime",
    description="Система учёта рабочего времени юристов",
    version="1.0.0",
    debug=True
)

# Статические файлы (если добавишь css/js)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Шаблоны
#templates = Jinja2Templates(directory="app/templates")

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
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": None,           # ← добавьте эту строку
    })


router = APIRouter(prefix="", tags=["pages"])

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Пример статистики (адаптируй под свои модели)
    stats = {
        "active_matters": db.query(Matter).filter(Matter.status == "open").count(),
        "pending_time_entries": db.query(TimeEntry).filter(TimeEntry.status == "draft").count(),
        "total_hours_this_month": 0,  # можно посчитать реально
        "clients_count": db.query(Client).count(),
    }

    # Последние 5 таймшитов/активностей (для примера)
    recent_activities = (
        db.query(TimeEntry)
        .order_by(TimeEntry.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "recent_activities": recent_activities,
        }
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

@app.get("/debug-routes")
def debug_routes():
    routes_info = []
    for route in app.routes:
        if hasattr(route, "name") and route.name:
            info = {
                "name": route.name,
                "path": route.path if hasattr(route, "path") else "(mounted)",
                "methods": list(route.methods) if hasattr(route, "methods") and route.methods else None
            }
            routes_info.append(info)
    return routes_info