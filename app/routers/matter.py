from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.matter import matter as crud_matter
from app.schemas.matter import Matter, MatterCreate
from app.utils.auth import get_current_admin_user, get_current_user

router = APIRouter(prefix="/matters", tags=["matters"])

@router.post("/", response_model=Matter, status_code=status.HTTP_201_CREATED)
def create_matter(
    matter_in: MatterCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    # Создаём дело
    new_matter = crud_matter.create(db, obj_in=matter_in.dict())

    # Попытка создать событие в Google Calendar, если пользователь подключил календарь
    credentials = get_google_credentials(db, current_user.id)
    if credentials:
        try:
            service = build("calendar", "v3", credentials=credentials)

            event = {
                "summary": f"Дело: {new_matter.code} {new_matter.name}",
                "description": (
                    f"Код дела: {new_matter.code}\n"
                    f"Описание: {new_matter.description or 'Нет описания'}\n"
                    f"Ссылка в LegalTime: http://127.0.0.1:8000/matters/{new_matter.id}"
                ),
                "start": {
                    "dateTime": datetime.utcnow().isoformat() + "Z",
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
                    "timeZone": "UTC",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 30},
                    ],
                },
            }

            service.events().insert(calendarId="primary", body=event).execute()
            print("Подключён календарь:", credentials is not None)
            # Можно добавить лог или уведомление, что событие создано
        except Exception as e:
            # Не падаем, если календарь не работает — это дополнительная фича
            print(f"Не удалось создать событие в Google Calendar: {e}")

    return new_matter

@router.get("/", response_model=list[Matter])
def read_matters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Все авторизованные могут читать
):
    """Получить список дел - доступно всем авторизованным пользователям"""
    return crud_matter.get_multi(db, skip=skip, limit=limit)

@router.get("/{matter_id}", response_model=Matter)
def read_matter(
    matter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Все авторизованные могут читать
):
    """Получить дело по ID - доступно всем авторизованным пользователям"""
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return db_matter

@router.put("/{matter_id}", response_model=Matter)
def update_matter(
    matter_id: int,
    matter_in: MatterCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return crud_matter.update(db, db_obj=db_matter, obj_in=matter_in.dict())

@router.delete("/{matter_id}", response_model=Matter)
def delete_matter(
    matter_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return crud_matter.remove(db, id=matter_id)