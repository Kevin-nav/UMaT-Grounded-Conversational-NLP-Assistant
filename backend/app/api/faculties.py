from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import DbDep
from app.core.rbac import require_roles
from app.db.models import Department, Faculty
from app.schemas.faculty import FacultyCreate, FacultyRead, FacultyUpdate


router = APIRouter(prefix="/faculties", tags=["faculties"])
EditorDep = Annotated[object, Depends(require_roles("super_admin", "editor"))]


@router.get("", response_model=list[FacultyRead])
def list_faculties(db: DbDep) -> list[Faculty]:
    return db.scalars(select(Faculty).order_by(Faculty.name)).all()


@router.post("", response_model=FacultyRead)
def create_faculty(payload: FacultyCreate, db: DbDep, _: EditorDep) -> Faculty:
    faculty = Faculty(**payload.model_dump())
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty


@router.patch("/{faculty_id}", response_model=FacultyRead)
def update_faculty(faculty_id: str, payload: FacultyUpdate, db: DbDep, _: EditorDep) -> Faculty:
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(faculty, key, value)
    db.commit()
    db.refresh(faculty)
    return faculty


@router.delete("/{faculty_id}")
def delete_faculty(faculty_id: str, db: DbDep, _: EditorDep) -> dict[str, str]:
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    if db.scalar(select(Department.id).where(Department.faculty_id == faculty_id).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Faculty still has departments")
    db.delete(faculty)
    db.commit()
    return {"message": "Faculty deleted"}

