from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMModel


class DepartmentBase(BaseModel):
    id: str
    faculty_id: str | None = None
    name: str
    aliases: list[str] = []
    campus: str | None = None
    location_guide: str | None = None
    notes: str | None = None


class DepartmentRead(DepartmentBase, ORMModel):
    pass


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    faculty_id: str | None = None
    name: str | None = None
    aliases: list[str] | None = None
    campus: str | None = None
    location_guide: str | None = None
    notes: str | None = None
