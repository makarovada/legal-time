from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.client import client as crud_client
from app.schemas.client import Client, ClientCreate
from app.utils.auth import get_current_admin_user

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud_client.create(db, obj_in=client_in.dict())

@router.get("/", response_model=list[Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    clients = crud_client.get_multi(db, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=Client)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_client = crud_client.get(db, id=client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.put("/{client_id}", response_model=Client)
def update_client(
    client_id: int,
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_client = crud_client.get(db, id=client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud_client.update(db, db_obj=db_client, obj_in=client_in.dict())

@router.delete("/{client_id}", response_model=Client)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_client = crud_client.get(db, id=client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud_client.remove(db, id=client_id)