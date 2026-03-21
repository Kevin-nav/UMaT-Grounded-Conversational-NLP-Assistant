from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMModel


class FacultyBase(BaseModel):
    id: str
    name: str
    short_name: str | None = None
    campus: str | None = None
    description: str | None = None


class FacultyRead(FacultyBase, ORMModel):
    pass


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    campus: str | None = None
    description: str | None = None
