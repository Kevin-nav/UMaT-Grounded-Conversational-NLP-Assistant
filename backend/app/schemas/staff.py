from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMModel


class StaffBase(BaseModel):
    id: str
    full_name: str
    title: str | None = None
    rank_role: str | None = None
    faculty_id: str | None = None
    department_id: str | None = None
    campus: str | None = None
    specializations: list[str] = []
    bio: str | None = None
    aliases: list[str] = []
    source_section: str | None = None
    source_notes: str | None = None
    is_active: bool = True


class StaffRead(StaffBase, ORMModel):
    pass


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    full_name: str | None = None
    title: str | None = None
    rank_role: str | None = None
    faculty_id: str | None = None
    department_id: str | None = None
    campus: str | None = None
    specializations: list[str] | None = None
    bio: str | None = None
    aliases: list[str] | None = None
    source_section: str | None = None
    source_notes: str | None = None
    is_active: bool | None = None
