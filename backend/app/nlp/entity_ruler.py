from __future__ import annotations

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler

from app.db.models import Department, Faculty, StaffMember


def build_nlp(staff: list[StaffMember], departments: list[Department], faculties: list[Faculty]) -> Language:
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    assert isinstance(ruler, EntityRuler)
    patterns = []
    for member in staff:
        patterns.append({"label": "PERSON", "pattern": member.full_name})
        for alias in member.aliases or []:
            patterns.append({"label": "PERSON", "pattern": alias})
        if member.rank_role:
            patterns.append({"label": "ROLE", "pattern": member.rank_role})
        for specialization in member.specializations or []:
            patterns.append({"label": "SPECIALIZATION", "pattern": specialization})
    for department in departments:
        patterns.append({"label": "DEPARTMENT", "pattern": department.name})
        for alias in department.aliases or []:
            patterns.append({"label": "DEPARTMENT", "pattern": alias})
    for faculty in faculties:
        patterns.append({"label": "FACULTY", "pattern": faculty.name})
        if faculty.short_name:
            patterns.append({"label": "FACULTY", "pattern": faculty.short_name})
    ruler.add_patterns(patterns)
    return nlp

