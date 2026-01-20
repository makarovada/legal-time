from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.time_entry import time_entry as crud_time_entry
from app.schemas.time_entry import TimeEntry, TimeEntryCreate
from app.utils.auth import get_current_user
from app.models.employee import Employee
from app.models.time_entry import TimeEntry as TimeEntryModel
from app.models.matter import Matter
from app.models.activity_type import ActivityType
from app.utils.google_calendar import (
    create_calendar_event,
    update_calendar_event,
    delete_calendar_event
)

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
    entry = crud_time_entry.create(db, obj_in=obj_in)
    
    # Синхронизация с Google Calendar
    if current_user.google_token_encrypted:
        try:
            matter = db.query(Matter).filter(Matter.id == entry.matter_id).first()
            activity_type = db.query(ActivityType).filter(ActivityType.id == entry.activity_type_id).first()
            if matter and activity_type:
                event_id = create_calendar_event(current_user, entry, matter, activity_type)
                if event_id:
                    entry.google_event_id = event_id
                    db.commit()
                    db.refresh(entry)
        except Exception as e:
            # Не прерываем создание таймшита, если синхронизация не удалась
            print(f"Failed to sync with Google Calendar: {e}")
    
    return entry

# Юрист видит только свои таймшиты
@router.get("/", response_model=list[TimeEntry])
def read_my_time_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entries = (
        db.query(TimeEntryModel)
        .filter(TimeEntryModel.employee_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
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
    updated_entry = crud_time_entry.update(db, db_obj=entry, obj_in=obj_in)
    
    # Синхронизация с Google Calendar
    employee = db.query(Employee).filter(Employee.id == updated_entry.employee_id).first()
    if employee and employee.google_token_encrypted:
        try:
            matter = db.query(Matter).filter(Matter.id == updated_entry.matter_id).first()
            activity_type = db.query(ActivityType).filter(ActivityType.id == updated_entry.activity_type_id).first()
            if matter and activity_type:
                if updated_entry.google_event_id:
                    # Обновляем существующее событие
                    event_id = update_calendar_event(employee, updated_entry, matter, activity_type, updated_entry.google_event_id)
                else:
                    # Создаем новое событие, если его не было
                    event_id = create_calendar_event(employee, updated_entry, matter, activity_type)
                    if event_id:
                        updated_entry.google_event_id = event_id
                        db.commit()
                        db.refresh(updated_entry)
        except Exception as e:
            print(f"Failed to sync with Google Calendar: {e}")
    
    return updated_entry

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
    
    # Удаляем событие из Google Calendar перед удалением таймшита
    employee = db.query(Employee).filter(Employee.id == entry.employee_id).first()
    if employee and employee.google_token_encrypted and entry.google_event_id:
        try:
            delete_calendar_event(employee, entry.google_event_id)
        except Exception as e:
            print(f"Failed to delete calendar event: {e}")
    
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
    
    # Обновляем событие в календаре при одобрении
    employee = db.query(Employee).filter(Employee.id == entry.employee_id).first()
    if employee and employee.google_token_encrypted and entry.google_event_id:
        try:
            matter = db.query(Matter).filter(Matter.id == entry.matter_id).first()
            activity_type = db.query(ActivityType).filter(ActivityType.id == entry.activity_type_id).first()
            if matter and activity_type:
                update_calendar_event(employee, entry, matter, activity_type, entry.google_event_id)
        except Exception as e:
            print(f"Failed to sync approval with Google Calendar: {e}")
    
    return entry


@router.post("/sync-to-calendar", response_model=dict)
def sync_all_entries_to_calendar(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Синхронизировать все существующие таймшиты с Google Calendar"""
    if not current_user.google_token_encrypted:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Please connect your Google account first."
        )
    
    # Получаем все таймшиты пользователя без google_event_id
    entries = (
        db.query(TimeEntryModel)
        .filter(
            TimeEntryModel.employee_id == current_user.id,
            TimeEntryModel.google_event_id.is_(None)
        )
        .all()
    )
    
    synced_count = 0
    failed_count = 0
    
    for entry in entries:
        try:
            matter = db.query(Matter).filter(Matter.id == entry.matter_id).first()
            activity_type = db.query(ActivityType).filter(ActivityType.id == entry.activity_type_id).first()
            
            if matter and activity_type:
                event_id = create_calendar_event(current_user, entry, matter, activity_type)
                if event_id:
                    entry.google_event_id = event_id
                    synced_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"Failed to sync entry {entry.id}: {e}")
            failed_count += 1
    
    db.commit()
    
    return {
        "message": f"Sync completed",
        "synced": synced_count,
        "failed": failed_count,
        "total": len(entries)
    }


@router.get("/calendar/events")
def get_calendar_events(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
    max_results: int = 50
):
    """Получить события из Google Calendar, связанные с таймшитами"""
    from app.utils.google_calendar import get_calendar_service
    from datetime import datetime, timedelta
    from googleapiclient.errors import HttpError
    
    if not current_user.google_token_encrypted:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Please connect your Google account first."
        )
    
    service = get_calendar_service(current_user)
    if not service:
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to Google Calendar service"
        )
    
    calendar_id = current_user.google_calendar_id or 'primary'
    
    # Получаем события за последние 30 дней и следующие 30 дней
    time_min = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
    time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
    
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Фильтруем только события, связанные с таймшитами
        time_entry_events = []
        for event in events:
            # Проверяем, есть ли это событие в нашей БД
            entry = db.query(TimeEntryModel).filter(
                TimeEntryModel.google_event_id == event.get('id')
            ).first()
            
            if entry:
                time_entry_events.append({
                    'event_id': event.get('id'),
                    'summary': event.get('summary'),
                    'description': event.get('description'),
                    'start': event.get('start'),
                    'end': event.get('end'),
                    'time_entry_id': entry.id,
                    'status': entry.status
                })
        
        return {
            'events': time_entry_events,
            'total': len(time_entry_events)
        }
    except HttpError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch calendar events: {str(e)}"
        )