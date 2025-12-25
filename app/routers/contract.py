from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.contract import contract as crud_contract
from app.schemas.contract import Contract, ContractCreate
from app.utils.auth import get_current_admin_user  # пока только админ

router = APIRouter(prefix="/contracts", tags=["contracts"])

@router.post("/", response_model=Contract, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract_in: ContractCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud_contract.create(db, obj_in=contract_in.dict())

@router.get("/", response_model=list[Contract])
def read_contracts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud_contract.get_multi(db, skip=skip, limit=limit)

@router.get("/{contract_id}", response_model=Contract)
def read_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_contract = crud_contract.get(db, id=contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return db_contract

@router.put("/{contract_id}", response_model=Contract)
def update_contract(
    contract_id: int,
    contract_in: ContractCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_contract = crud_contract.get(db, id=contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return crud_contract.update(db, db_obj=db_contract, obj_in=contract_in.dict())

@router.delete("/{contract_id}", response_model=Contract)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_contract = crud_contract.get(db, id=contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return crud_contract.remove(db, id=contract_id)