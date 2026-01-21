from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
import json

# Scopes для Google Calendar API
# ВАЖНО: Эти scopes должны совпадать с настройками в Google Cloud Console
# Если вы изменили scopes в Google Cloud Console, обновите их здесь тоже
# Для создания календарей нужен полный доступ calendar, calendar.readonly не нужен
SCOPES = [
    'https://www.googleapis.com/auth/calendar',  # Полный доступ, включая создание календарей
    'https://www.googleapis.com/auth/calendar.events'  # Управление событиями
]


def get_fernet() -> Optional[Fernet]:
    """Получить Fernet для шифрования/расшифровки токенов"""
    if not settings.FERNET_KEY:
        return None
    return Fernet(settings.FERNET_KEY.encode())


def encrypt_token(token: str) -> Optional[str]:
    """Зашифровать токен"""
    fernet = get_fernet()
    if not fernet:
        return None
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: Optional[str]) -> Optional[str]:
    """Расшифровать токен"""
    if not encrypted_token:
        return None
    fernet = get_fernet()
    if not fernet:
        return None
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return None


def get_google_credentials(employee) -> Optional[Credentials]:
    """Получить Google Credentials из зашифрованных токенов сотрудника"""
    if not employee.google_token_encrypted:
        return None
    
    token_json = decrypt_token(employee.google_token_encrypted)
    if not token_json:
        return None
    
    try:
        token_data = json.loads(token_json)
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=decrypt_token(employee.google_refresh_token_encrypted),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        
        # Проверяем и обновляем токен, если нужно
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception:
                pass  # Если не удалось обновить, вернем истекший токен
        
        return credentials
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None


def get_calendar_service(employee) -> Optional[object]:
    """Получить сервис Google Calendar API"""
    credentials = get_google_credentials(employee)
    if not credentials:
        return None
    try:
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error building calendar service: {e}")
        return None


def create_calendar_event(employee, time_entry, matter, activity_type) -> Optional[str]:
    """Создать событие в Google Calendar для таймшита"""
    service = get_calendar_service(employee)
    if not service:
        return None
    
    calendar_id = employee.google_calendar_id or 'primary'
    
    # Формируем название события
    event_title = f"{matter.code} - {matter.name}"
    if activity_type:
        event_title += f" ({activity_type.name})"
    
    # Вычисляем время начала и конца
    start_datetime = datetime.combine(time_entry.date, datetime.min.time())
    end_datetime = start_datetime + timedelta(hours=time_entry.hours)
    
    # Описание события
    description = f"Часы: {time_entry.hours}\n"
    if time_entry.description:
        description += f"Описание: {time_entry.description}\n"
    description += f"Статус: {time_entry.status}"
    
    event = {
        'summary': event_title,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    try:
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        return event_result.get('id')
    except HttpError as e:
        print(f"Error creating calendar event: {e}")
        return None


def update_calendar_event(employee, time_entry, matter, activity_type, event_id: str) -> Optional[str]:
    """Обновить событие в Google Calendar"""
    service = get_calendar_service(employee)
    if not service:
        return None
    
    calendar_id = employee.google_calendar_id or 'primary'
    
    # Получаем существующее событие
    try:
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    except HttpError as e:
        print(f"Error getting calendar event: {e}")
        return None
    
    # Обновляем данные события
    event_title = f"{matter.code} - {matter.name}"
    if activity_type:
        event_title += f" ({activity_type.name})"
    
    start_datetime = datetime.combine(time_entry.date, datetime.min.time())
    end_datetime = start_datetime + timedelta(hours=time_entry.hours)
    
    description = f"Часы: {time_entry.hours}\n"
    if time_entry.description:
        description += f"Описание: {time_entry.description}\n"
    description += f"Статус: {time_entry.status}"
    
    event['summary'] = event_title
    event['description'] = description
    event['start'] = {
        'dateTime': start_datetime.isoformat(),
        'timeZone': 'UTC',
    }
    event['end'] = {
        'dateTime': end_datetime.isoformat(),
        'timeZone': 'UTC',
    }
    
    try:
        updated_event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        return updated_event.get('id')
    except HttpError as e:
        print(f"Error updating calendar event: {e}")
        return None


def delete_calendar_event(employee, event_id: str) -> bool:
    """Удалить событие из Google Calendar"""
    service = get_calendar_service(employee)
    if not service:
        return False
    
    calendar_id = employee.google_calendar_id or 'primary'
    
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except HttpError as e:
        print(f"Error deleting calendar event: {e}")
        return False


def create_legal_time_calendar(employee) -> Optional[str]:
    """Создать отдельный календарь LegalTime для пользователя"""
    service = get_calendar_service(employee)
    if not service:
        return None
    
    try:
        calendar = {
            'summary': 'LegalTime',
            'description': 'Календарь для учета времени и задач юридической практики',
            'timeZone': 'UTC'
        }
        
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar.get('id')
        return calendar_id
    except HttpError as e:
        print(f"Error creating calendar: {e}")
        return None


def get_google_oauth_flow(redirect_uri: str) -> Flow:
    """Создать OAuth flow для авторизации Google"""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow


def get_calendar_events(employee, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, max_results: int = 100) -> list:
    """Получить события из Google Calendar за указанный период"""
    service = get_calendar_service(employee)
    if not service:
        return []
    
    calendar_id = employee.google_calendar_id or 'primary'
    
    # По умолчанию получаем события за последние 30 дней и следующие 30 дней
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow() + timedelta(days=30)
    
    time_min = start_date.isoformat() + 'Z'
    time_max = end_date.isoformat() + 'Z'
    
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except HttpError as e:
        print(f"Error fetching calendar events: {e}")
        return []

