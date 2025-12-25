from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee as EmployeeModel # <-- модель SQLAlchemy
from app.schemas.employee import EmployeeCreate, Employee  # <-- Pydantic-схемы
from app.utils.auth import get_password_hash, get_current_admin_user

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    if db.query(EmployeeModel).filter(EmployeeModel.email == employee_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(employee_in.password)
    db_employee = EmployeeModel(
        name=employee_in.name,
        email=employee_in.email,
        password_hash=hashed_password,
        role=employee_in.role
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee  # возвращаем Pydantic-схему автоматически

@router.get("/", response_model=list[Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
    return employees