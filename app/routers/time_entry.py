from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.time_entry import time_entry as crud_time_entry
from app.schemas.time_entry import TimeEntry, TimeEntryCreate
from app.utils.auth import get_current_user
from app.models.employee import Employee

router = APIRouter(prefix="/time-entries", tags=["time-entries"])

# Юрист создаёт только свои таймшиты
@router.post("/", response_model=TimeEntry, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    time_entry_in: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    # Принудительно привязываем к текущему пользователю
    obj_in = time_entry_in.dict()
    obj_in["employee_id"] = current_user.id
    return crud_time_entry.create(db, obj_in=obj_in)

# Юрист видит только свои таймшиты
@router.get("/", response_model=list[TimeEntry])
def read_my_time_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entries = db.query(TimeEntry).filter(TimeEntry.employee_id == current_user.id).offset(skip).limit(limit).all()
    return entries

# Админ/старший видит все (или по фильтру — потом доработаем)
@router.get("/all", response_model=list[TimeEntry])
def read_all_time_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)  # пока только админ
):
    return crud_time_entry.get_multi(db, skip=skip, limit=limit)

@router.get("/{entry_id}", response_model=TimeEntry)
def read_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.employee_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return entry

# Удаление и редактирование — только свои или админ
@router.put("/{entry_id}", response_model=TimeEntry)
def update_time_entry(
    entry_id: int,
    time_entry_in: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.employee_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    obj_in = time_entry_in.dict()
    obj_in["employee_id"] = entry.employee_id  # нельзя менять владельца
    return crud_time_entry.update(db, db_obj=entry, obj_in=obj_in)

@router.delete("/{entry_id}", response_model=TimeEntry)
def delete_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.employee_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud_time_entry.remove(db, id=entry_id)

@router.patch("/{entry_id}/approve", response_model=TimeEntry)
def approve_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    # Только админ или старший юрист (расширим позже)
    if current_user.role not in ["admin", "senior_lawyer"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    entry.status = "approved"
    db.commit()
    db.refresh(entry)
    return entry
# from .. import schemas, crud  # ваши модели и CRUD

@router.get("/stats")
def get_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Здесь ваша логика с учётом current_user (например, статистика только по его сотруднику)
    total_hours = 150.0
    pending = 7
    return {"totalHours": total_hours, "pendingTimesheets": pending}