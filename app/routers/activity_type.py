from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.activity_type import activity_type as crud_activity_type
from app.schemas.activity_type import ActivityType, ActivityTypeCreate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/activity-types", tags=["activity-types"])

@router.get("/", response_model=list[ActivityType])
def read_activity_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список всех типов активности"""
    return crud_activity_type.get_multi(db, skip=skip, limit=limit)

@router.get("/{activity_type_id}", response_model=ActivityType)
def read_activity_type(
    activity_type_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить тип активности по ID"""
    db_activity_type = crud_activity_type.get(db, id=activity_type_id)
    if not db_activity_type:
        raise HTTPException(status_code=404, detail="Activity type not found")
    return db_activity_type


