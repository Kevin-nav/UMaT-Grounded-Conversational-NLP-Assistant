from __future__ import annotations

from app.db.models import Department, Faculty, LocationGuide, StaffMember


def build_staff_answer(member: StaffMember, location_guide: LocationGuide | None) -> str:
    base = member.full_name
    if member.title:
        base = f"{member.title} {base}"
    details = [member.rank_role] if member.rank_role else []
    if member.specializations:
        details.append(f"specializes in {', '.join(member.specializations[:4])}")
    response = f"{base}"
    if details:
        response += f" is {details[0]}"
        if len(details) > 1:
            response += f" and {details[1]}"
        response += "."
    if location_guide:
        response += f" Office guidance: {location_guide.directions_text}"
    return response


def build_department_answer(department: Department, faculty: Faculty | None, guide: LocationGuide | None) -> str:
    faculty_fragment = f" under {faculty.name}" if faculty else ""
    response = f"{department.name} is based on the {department.campus}{faculty_fragment}."
    if guide:
        response += f" {guide.directions_text}"
    elif department.location_guide:
        response += f" {department.location_guide}"
    return response

