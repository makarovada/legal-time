from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee as EmployeeModel # <-- модель SQLAlchemy
from app.schemas.employee import EmployeeCreate, Employee  # <-- Pydantic-схемы
from app.utils.auth import get_password_hash, get_current_admin_user, get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    if db.query(EmployeeModel).filter(EmployeeModel.email == employee_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not employee_in.password or not employee_in.password.strip():
        raise HTTPException(status_code=400, detail="Password is required")
    
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
    current_user = Depends(get_current_user)
):
    """Получить список сотрудников - доступно всем авторизованным пользователям"""
    employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
    return employees

@router.get("/{employee_id}", response_model=Employee)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить сотрудника по ID - доступно всем авторизованным пользователям"""
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Обновить сотрудника - доступно только администраторам"""
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Проверка уникальности email (если изменился)
    if employee_in.email != employee.email:
        if db.query(EmployeeModel).filter(EmployeeModel.email == employee_in.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Обновляем данные
    employee.name = employee_in.name
    employee.email = employee_in.email
    employee.role = employee_in.role
    
    # Обновляем пароль только если он указан и не пустой
    if employee_in.password and employee_in.password.strip():
        employee.password_hash = get_password_hash(employee_in.password)
    
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{employee_id}", response_model=Employee)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Удалить сотрудника - доступно только администраторам"""
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Нельзя удалить самого себя
    if employee.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(employee)
    db.commit()
    return employee