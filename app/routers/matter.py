from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.matter import matter as crud_matter
from app.schemas.matter import Matter, MatterCreate
from app.utils.auth import get_current_admin_user

router = APIRouter(prefix="/matters", tags=["matters"])

@router.post("/", response_model=Matter, status_code=status.HTTP_201_CREATED)
def create_matter(
    matter_in: MatterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud_matter.create(db, obj_in=matter_in.dict())

@router.get("/", response_model=list[Matter])
def read_matters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud_matter.get_multi(db, skip=skip, limit=limit)

@router.get("/{matter_id}", response_model=Matter)
def read_matter(
    matter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return db_matter

@router.put("/{matter_id}", response_model=Matter)
def update_matter(
    matter_id: int,
    matter_in: MatterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return crud_matter.update(db, db_obj=db_matter, obj_in=matter_in.dict())

@router.delete("/{matter_id}", response_model=Matter)
def delete_matter(
    matter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_matter = crud_matter.get(db, id=matter_id)
    if not db_matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return crud_matter.remove(db, id=matter_id)