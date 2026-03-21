from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Department, Faculty, LocationGuide, StaffMember


def _staff_record(member: StaffMember) -> dict[str, object]:
    return {
        "entity_id": member.id,
        "entity_type": "staff",
        "display_name": member.full_name,
        "aliases": list(member.aliases or []),
        "facts": {
            "title": member.title,
            "role": member.rank_role,
            "faculty_id": member.faculty_id,
            "department_id": member.department_id,
            "campus": member.campus,
            "specializations": list(member.specializations or []),
            "bio": member.bio,
            "source_section": member.source_section,
            "source_notes": member.source_notes,
            "is_active": member.is_active,
        },
    }


def _department_record(department: Department) -> dict[str, object]:
    return {
        "entity_id": department.id,
        "entity_type": "department",
        "display_name": department.name,
        "aliases": list(department.aliases or []),
        "facts": {
            "faculty_id": department.faculty_id,
            "campus": department.campus,
            "location_guide": department.location_guide,
            "notes": department.notes,
        },
    }


def _faculty_record(faculty: Faculty) -> dict[str, object]:
    aliases = [faculty.short_name] if faculty.short_name else []
    return {
        "entity_id": faculty.id,
        "entity_type": "faculty",
        "display_name": faculty.name,
        "aliases": aliases,
        "facts": {
            "short_name": faculty.short_name,
            "campus": faculty.campus,
            "description": faculty.description,
        },
    }


def _location_guide_record(guide: LocationGuide) -> dict[str, object]:
    return {
        "entity_id": guide.id,
        "entity_type": "location_guide",
        "display_name": guide.id.replace("-", " "),
        "aliases": [],
        "facts": {
            "faculty_id": guide.faculty_id,
            "department_id": guide.department_id,
            "campus": guide.campus,
            "directions_text": guide.directions_text,
        },
    }


def _serialize(items: Sequence[object], serializer) -> list[dict[str, object]]:
    return [serializer(item) for item in items]


def export_canonical_dataset(db: Session) -> dict[str, list[dict[str, object]]]:
    staff = db.scalars(select(StaffMember).order_by(StaffMember.full_name)).all()
    departments = db.scalars(select(Department).order_by(Department.name)).all()
    faculties = db.scalars(select(Faculty).order_by(Faculty.name)).all()
    location_guides = db.scalars(select(LocationGuide).order_by(LocationGuide.id)).all()

    return {
        "staff": _serialize(staff, _staff_record),
        "departments": _serialize(departments, _department_record),
        "faculties": _serialize(faculties, _faculty_record),
        "location_guides": _serialize(location_guides, _location_guide_record),
    }
