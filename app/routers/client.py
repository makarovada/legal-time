from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.client import client as crud_client
from app.schemas.client import Client, ClientCreate
from app.utils.auth import get_current_admin_user, get_current_user

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
    current_user = Depends(get_current_user)  # Все авторизованные могут читать
):
    """Получить список клиентов - доступно всем авторизованным пользователям"""
    clients = crud_client.get_multi(db, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=Client)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Все авторизованные могут читать
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
    
    # Проверяем, есть ли связанные договоры
    if db_client.contracts:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete client: client has {len(db_client.contracts)} associated contract(s). Delete contracts first."
        )
    
    try:
        return crud_client.remove(db, id=client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")