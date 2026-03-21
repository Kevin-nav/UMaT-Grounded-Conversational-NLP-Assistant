from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMModel


class LocationGuideBase(BaseModel):
    id: str
    faculty_id: str | None = None
    department_id: str | None = None
    campus: str | None = None
    directions_text: str


class LocationGuideRead(LocationGuideBase, ORMModel):
    pass


class LocationGuideCreate(LocationGuideBase):
    pass


class LocationGuideUpdate(BaseModel):
    faculty_id: str | None = None
    department_id: str | None = None
    campus: str | None = None
    directions_text: str | None = None
