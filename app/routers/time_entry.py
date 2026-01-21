from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.time_entry import time_entry as crud_time_entry
from app.schemas.time_entry import TimeEntry, TimeEntryCreate
from app.utils.auth import get_current_user, get_current_admin_user, get_current_senior_lawyer_or_admin
from app.models.employee import Employee
from app.models.time_entry import TimeEntry as TimeEntryModel
from app.models.matter import Matter
from app.models.activity_type import ActivityType
from app.models.contract import Contract
from app.models.client import Client
from app.models.rate import Rate
from app.utils.google_calendar import (
    create_calendar_event,
    update_calendar_event,
    delete_calendar_event
)
from datetime import datetime
from io import BytesIO
import openpyxl

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


def _resolve_rate(db: Session, employee_id: int, matter_id: int) -> Rate | None:
    """
    Определение ставки с приоритетом:
    1) ставка по договору (contract_id)
    2) индивидуальная ставка сотрудника (employee_id)
    3) дефолтная ставка (оба поля None)
    """
    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    contract_id = matter.contract_id if matter else None

    # 1. Ставка по договору
    if contract_id:
        contract_rate = (
            db.query(Rate)
            .filter(Rate.contract_id == contract_id, Rate.employee_id.is_(None))
            .first()
        )
        if contract_rate:
            return contract_rate

    # 2. Индивидуальная ставка сотрудника
    employee_rate = (
        db.query(Rate)
        .filter(Rate.employee_id == employee_id, Rate.contract_id.is_(None))
        .first()
    )
    if employee_rate:
        return employee_rate

    # 3. Дефолтная ставка
    default_rate = (
        db.query(Rate)
        .filter(Rate.employee_id.is_(None), Rate.contract_id.is_(None))
        .first()
    )
    # Если дефолтной ещё нет — создаём её со значением 3000
    if not default_rate:
        default_rate = Rate(
            value=3000.0,
            employee_id=None,
            contract_id=None,
        )
        db.add(default_rate)
        db.commit()
        db.refresh(default_rate)

    return default_rate


@router.post("/recalculate-rates", response_model=dict)
def recalculate_time_entry_rates(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
):
    """
    Пересчитать ставки для всех существующих таймшитов
    по приоритету:
    1) ставка по договору
    2) индивидуальная ставка сотрудника
    3) дефолтная ставка (3000, создаётся автоматически при отсутствии)
    """
    entries = db.query(TimeEntryModel).all()
    updated = 0

    for entry in entries:
        rate = _resolve_rate(db, employee_id=entry.employee_id, matter_id=entry.matter_id)
        new_rate_id = rate.id if rate else None
        if entry.rate_id != new_rate_id:
            entry.rate_id = new_rate_id
            updated += 1

    db.commit()

    return {
        "message": "Rates recalculated for time entries",
        "updated": updated,
        "total": len(entries),
    }


@router.get("/report")
def export_time_entries_report(
    employee_id: int | None = None,
    matter_id: int | None = None,
    contract_id: int | None = None,
    client_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_senior_lawyer_or_admin),
):
    """
    Выгрузка отчёта по ОДОБРЕННЫМ таймшитам в Excel с фильтрами:
    - по сотруднику
    - по делу
    - по договору
    - по клиенту
    - по периоду дат
    Доступно только старшим юристам и администраторам.
    """
    query = (
        db.query(TimeEntryModel)
        .join(Employee, TimeEntryModel.employee_id == Employee.id)
        .join(Matter, TimeEntryModel.matter_id == Matter.id)
        .join(Contract, Matter.contract_id == Contract.id)
        .join(Client, Contract.client_id == Client.id)
        .join(ActivityType, TimeEntryModel.activity_type_id == ActivityType.id)
        .outerjoin(Rate, TimeEntryModel.rate_id == Rate.id)
        .filter(TimeEntryModel.status == "approved")
    )

    # Фильтры
    if employee_id:
        query = query.filter(TimeEntryModel.employee_id == employee_id)
    if matter_id:
        query = query.filter(TimeEntryModel.matter_id == matter_id)
    if contract_id:
        query = query.filter(Matter.contract_id == contract_id)
    if client_id:
        query = query.filter(Contract.client_id == client_id)

    if start_date:
        try:
            start = datetime.fromisoformat(start_date).date()
            query = query.filter(TimeEntryModel.date >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.fromisoformat(end_date).date()
            query = query.filter(TimeEntryModel.date <= end)
        except ValueError:
            pass

    entries = query.all()

    # Создаём Excel-файл
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчёт по времени"

    headers = [
        "Дата",
        "Сотрудник",
        "Клиент",
        "Договор",
        "Дело",
        "Тип активности",
        "Часы",
        "Ставка",
        "Сумма",
        "Статус",
        "Описание",
    ]
    ws.append(headers)

    for entry in entries:
        # Благодаря join'ам у нас уже загружены связанные сущности
        employee = entry.employee
        matter = entry.matter
        contract = matter.contract if matter else None
        client = contract.client if contract else None
        activity_type = entry.activity_type if hasattr(entry, "activity_type") else None

        rate_value = None
        if entry.rate is not None:
            rate_value = entry.rate.value
        elif hasattr(entry, "rate_value") and entry.rate_value is not None:
            rate_value = entry.rate_value

        amount = (entry.hours or 0) * (rate_value or 0)

        ws.append(
            [
                entry.date.isoformat() if entry.date else "",
                employee.name if employee else "",
                client.name if client else "",
                contract.number if contract else "",
                f"{matter.code} - {matter.name}" if matter else "",
                activity_type.name if activity_type else "",
                entry.hours,
                rate_value,
                amount,
                entry.status,
                entry.description or "",
            ]
        )

    # Немного формата: ширина колонок
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                max_len = max(max_len, len(str(cell.value)) if cell.value is not None else 0)
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 2, 50)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"time_entries_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

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

    # Определяем ставку по приоритету:
    # 1) ставка по договору
    # 2) индивидуальная ставка сотрудника
    # 3) дефолтная ставка
    rate = _resolve_rate(db, employee_id=current_user.id, matter_id=obj_in["matter_id"])
    obj_in["rate_id"] = rate.id if rate else None

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

# Старший юрист и админ могут фильтровать таймшиты по сотруднику и периоду
@router.get("/filter", response_model=list[TimeEntry])
def filter_time_entries(
    employee_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_senior_lawyer_or_admin)
):
    """Фильтрация таймшитов по сотруднику и периоду - доступно старшим юристам и администраторам"""
    from datetime import datetime
    
    query = db.query(TimeEntryModel)
    
    # Фильтр по сотруднику
    if employee_id:
        query = query.filter(TimeEntryModel.employee_id == employee_id)
    
    # Фильтр по дате начала
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(TimeEntryModel.date >= start_dt.date())
        except ValueError:
            pass
    
    # Фильтр по дате окончания
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(TimeEntryModel.date <= end_dt.date())
        except ValueError:
            pass
    
    # Фильтр по статусу
    if status:
        query = query.filter(TimeEntryModel.status == status)
    
    entries = query.offset(skip).limit(limit).all()
    return entries

# Таймшиты на одобрение (для старших юристов и админов)
@router.get("/pending", response_model=list[TimeEntry])
def read_pending_time_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_senior_lawyer_or_admin)
):
    """Получить таймшиты на одобрение - доступно старшим юристам и администраторам"""
    entries = (
        db.query(TimeEntryModel)
        .filter(TimeEntryModel.status == "draft")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return entries

@router.get("/{entry_id}", response_model=TimeEntry)
def read_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.employee_id != current_user.id and current_user.role not in ["admin", "senior_lawyer"]:
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
    if entry.employee_id != current_user.id and current_user.role not in ["admin", "senior_lawyer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    obj_in = time_entry_in.dict()
    obj_in["employee_id"] = entry.employee_id  # нельзя менять владельца

    # Переопределяем ставку по тем же правилам при изменении дела / сотрудника
    rate = _resolve_rate(db, employee_id=entry.employee_id, matter_id=obj_in["matter_id"])
    obj_in["rate_id"] = rate.id if rate else None
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
    if entry.employee_id != current_user.id and current_user.role not in ["admin", "senior_lawyer"]:
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
    current_user: Employee = Depends(get_current_senior_lawyer_or_admin)
):
    """Одобрить таймшит - доступно старшим юристам и администраторам"""
    entry = crud_time_entry.get(db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    # Старший юрист не может одобрить свой собственный таймшит через этот эндпоинт
    # (должен использовать фильтр для просмотра всех таймшитов, включая свои)
    if current_user.role == "senior_lawyer" and entry.employee_id == current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Senior lawyers cannot approve their own time entries through this endpoint. Use the filter endpoint to view and approve your entries."
        )
    
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


@router.post("/sync-from-calendar", response_model=dict)
def sync_from_calendar(
    days_back: int = 30,
    days_forward: int = 30,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Синхронизировать события из Google Calendar в таймшиты.
    Создает новые таймшиты для событий, которых еще нет в системе.
    """
    from app.utils.google_calendar import get_calendar_events
    from datetime import datetime, timedelta, date
    import re
    
    if not current_user.google_token_encrypted:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Please connect your Google account first."
        )
    
    # Получаем события из календаря
    start_date = datetime.utcnow() - timedelta(days=days_back)
    end_date = datetime.utcnow() + timedelta(days=days_forward)
    events = get_calendar_events(current_user, start_date, end_date, max_results=500)
    
    if not events:
        return {
            "message": "No events found in calendar",
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "total": 0
        }
    
    # Получаем дефолтный тип активности (первый доступный или "Консультация")
    default_activity_type = db.query(ActivityType).filter(ActivityType.name == "Консультация").first()
    if not default_activity_type:
        default_activity_type = db.query(ActivityType).first()
    if not default_activity_type:
        raise HTTPException(
            status_code=500,
            detail="No activity types found in database"
        )
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for event in events:
        event_id = event.get('id')
        if not event_id:
            continue
        
        # Проверяем, есть ли уже таймшит с таким google_event_id
        existing_entry = db.query(TimeEntryModel).filter(
            TimeEntryModel.google_event_id == event_id
        ).first()
        
        if existing_entry:
            skipped_count += 1
            continue
        
        try:
            # Парсим данные события
            summary = event.get('summary', '')
            description = event.get('description', '')
            start = event.get('start', {})
            end = event.get('end', {})
            
            # Извлекаем дату и время
            start_datetime_str = start.get('dateTime') or start.get('date')
            end_datetime_str = end.get('dateTime') or end.get('date')
            
            if not start_datetime_str or not end_datetime_str:
                failed_count += 1
                continue
            
            # Парсим дату и время
            if 'T' in start_datetime_str:
                start_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
                entry_date = start_dt.date()
                hours = (end_dt - start_dt).total_seconds() / 3600.0
            else:
                # Если только дата без времени
                start_dt = datetime.fromisoformat(start_datetime_str)
                end_dt = datetime.fromisoformat(end_datetime_str)
                entry_date = start_dt.date()
                hours = 1.0  # По умолчанию 1 час для событий без времени
            
            # Пытаемся найти дело по коду из названия события
            # Формат: "КОД - Название" или просто "КОД"
            matter = None
            if summary:
                # Пытаемся найти код дела в начале названия
                match = re.match(r'^([A-Z0-9-]+)', summary.strip())
                if match:
                    matter_code = match.group(1)
                    matter = db.query(Matter).filter(Matter.code == matter_code).first()
                
                # Если не нашли по коду, пытаемся найти по части названия
                if not matter:
                    for m in db.query(Matter).all():
                        if m.code in summary or m.name in summary:
                            matter = m
                            break
            
            # Если дело не найдено, пропускаем событие
            if not matter:
                failed_count += 1
                continue
            
            # Определяем ставку
            rate = _resolve_rate(db, employee_id=current_user.id, matter_id=matter.id)
            
            # Создаем таймшит
            new_entry = TimeEntryModel(
                employee_id=current_user.id,
                matter_id=matter.id,
                activity_type_id=default_activity_type.id,
                rate_id=rate.id if rate else None,
                hours=round(hours, 2),
                description=description or summary,
                date=entry_date,
                status="draft",
                google_event_id=event_id
            )
            
            db.add(new_entry)
            created_count += 1
            
        except Exception as e:
            print(f"Failed to create time entry from event {event.get('id')}: {e}")
            failed_count += 1
            continue
    
    db.commit()
    
    return {
        "message": "Sync from calendar completed",
        "created": created_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "total": len(events)
    }