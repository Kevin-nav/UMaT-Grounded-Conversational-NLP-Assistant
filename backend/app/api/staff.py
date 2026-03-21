from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select

from app.api.dependencies import DbDep
from app.core.rbac import require_roles
from app.db.models import StaffMember
from app.schemas.staff import StaffCreate, StaffRead, StaffUpdate


router = APIRouter(prefix="/staff", tags=["staff"])
EditorDep = Annotated[object, Depends(require_roles("super_admin", "editor"))]


@router.get("", response_model=list[StaffRead])
def list_staff(db: DbDep, search: str | None = Query(default=None)) -> list[StaffMember]:
    query = select(StaffMember).order_by(StaffMember.full_name)
    if search:
        query = query.where(
            or_(
                StaffMember.full_name.ilike(f"%{search}%"),
                StaffMember.rank_role.ilike(f"%{search}%"),
                StaffMember.bio.ilike(f"%{search}%"),
            )
        )
    return db.scalars(query).all()


@router.get("/{staff_id}", response_model=StaffRead)
def get_staff(staff_id: str, db: DbDep) -> StaffMember:
    staff = db.get(StaffMember, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return staff


@router.post("", response_model=StaffRead)
def create_staff(payload: StaffCreate, db: DbDep, _: EditorDep) -> StaffMember:
    staff = StaffMember(**payload.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.patch("/{staff_id}", response_model=StaffRead)
def update_staff(staff_id: str, payload: StaffUpdate, db: DbDep, _: EditorDep) -> StaffMember:
    staff = db.get(StaffMember, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}")
def delete_staff(staff_id: str, db: DbDep, _: EditorDep) -> dict[str, str]:
    staff = db.get(StaffMember, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    db.delete(staff)
    db.commit()
    return {"message": "Staff member deleted"}

