from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import DbDep
from app.core.rbac import require_roles
from app.db.models import LocationGuide
from app.schemas.location import LocationGuideCreate, LocationGuideRead, LocationGuideUpdate


router = APIRouter(prefix="/location-guides", tags=["locations"])
EditorDep = Annotated[object, Depends(require_roles("super_admin", "editor"))]


@router.get("", response_model=list[LocationGuideRead])
def list_location_guides(db: DbDep) -> list[LocationGuide]:
    return db.scalars(select(LocationGuide).order_by(LocationGuide.id)).all()


@router.post("", response_model=LocationGuideRead)
def create_location_guide(payload: LocationGuideCreate, db: DbDep, _: EditorDep) -> LocationGuide:
    location_guide = LocationGuide(**payload.model_dump())
    db.add(location_guide)
    db.commit()
    db.refresh(location_guide)
    return location_guide


@router.patch("/{guide_id}", response_model=LocationGuideRead)
def update_location_guide(guide_id: str, payload: LocationGuideUpdate, db: DbDep, _: EditorDep) -> LocationGuide:
    location_guide = db.get(LocationGuide, guide_id)
    if not location_guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location guide not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(location_guide, key, value)
    db.commit()
    db.refresh(location_guide)
    return location_guide


@router.delete("/{guide_id}")
def delete_location_guide(guide_id: str, db: DbDep, _: EditorDep) -> dict[str, str]:
    location_guide = db.get(LocationGuide, guide_id)
    if not location_guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location guide not found")
    db.delete(location_guide)
    db.commit()
    return {"message": "Location guide deleted"}

