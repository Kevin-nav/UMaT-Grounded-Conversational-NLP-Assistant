from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import DbDep
from app.core.rbac import require_roles
from app.db.models import Department, StaffMember
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate


router = APIRouter(prefix="/departments", tags=["departments"])
EditorDep = Annotated[object, Depends(require_roles("super_admin", "editor"))]


@router.get("", response_model=list[DepartmentRead])
def list_departments(db: DbDep) -> list[Department]:
    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post("", response_model=DepartmentRead)
def create_department(payload: DepartmentCreate, db: DbDep, _: EditorDep) -> Department:
    department = Department(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.patch("/{department_id}", response_model=DepartmentRead)
def update_department(department_id: str, payload: DepartmentUpdate, db: DbDep, _: EditorDep) -> Department:
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, key, value)
    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}")
def delete_department(department_id: str, db: DbDep, _: EditorDep) -> dict[str, str]:
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    if db.scalar(select(StaffMember.id).where(StaffMember.department_id == department_id).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department still has staff")
    db.delete(department)
    db.commit()
    return {"message": "Department deleted"}

