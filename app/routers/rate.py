from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.rate import rate as crud_rate
from app.schemas.rate import Rate, RateCreate
from app.utils.auth import get_current_senior_lawyer_or_admin


router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("/", response_model=List[Rate])
def read_rates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_senior_lawyer_or_admin),
):
    """
    Получить список ставок.
    Доступно старшим юристам и администраторам.
    """
    return crud_rate.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Rate, status_code=status.HTTP_201_CREATED)
def create_rate(
    rate_in: RateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_senior_lawyer_or_admin),
):
    """
    Создать ставку.
    Можно задать:
    - individual (employee_id != None, contract_id == None)
    - по договору (contract_id != None, employee_id == None)
    - дефолтную (оба None)
    """
    return crud_rate.create(db, obj_in=rate_in.dict())


@router.put("/{rate_id}", response_model=Rate)
def update_rate(
    rate_id: int,
    rate_in: RateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_senior_lawyer_or_admin),
):
    """
    Обновить ставку.
    """
    db_rate = crud_rate.get(db, id=rate_id)
    if not db_rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return crud_rate.update(db, db_obj=db_rate, obj_in=rate_in.dict())


@router.delete("/{rate_id}", response_model=Rate)
def delete_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_senior_lawyer_or_admin),
):
    """
    Удалить ставку.
    """
    db_rate = crud_rate.get(db, id=rate_id)
    if not db_rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return crud_rate.remove(db, id=rate_id)


