from __future__ import annotations

import re

from rapidfuzz import fuzz
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import Department, Faculty, LocationGuide, QueryLog, StaffMember
from app.nlp.entity_ruler import build_nlp
from app.nlp.intents import detect_intent
from app.nlp.normalize import normalize_query
from app.nlp.response_builder import build_department_answer, build_staff_answer
from app.schemas.chat import ChatQueryResponse, MatchItem


def _score(value: str, query: str) -> float:
    return float(fuzz.WRatio(value.lower(), query.lower()))


def _best_staff_score(member: StaffMember, query: str, intent: str) -> float:
    effective_query = query
    if intent == "role_lookup":
        effective_query = re.sub(r"^(who is|who s|tell me about)\s+", "", query).strip()
        effective_query = re.sub(r"^the\s+", "", effective_query).strip()
    elif intent == "specialization_lookup":
        effective_query = re.sub(r"^(who specializes in|who teaches|who researches?)\s+", "", query).strip()

    if intent == "role_lookup":
        candidates = [member.rank_role or ""]
    elif intent == "specialization_lookup":
        candidates = list(member.specializations or [])
    else:
        candidates = [member.full_name, *(member.aliases or []), member.rank_role or "", *(member.specializations or [])]

    best = 0.0
    normalized_query = effective_query.lower()
    for candidate in candidates:
        if not candidate:
            continue
        normalized_candidate = candidate.lower()
        score = _score(candidate, effective_query)
        if normalized_query in normalized_candidate:
            score = max(score, 100.0)
        elif intent == "role_lookup" and normalized_candidate in normalized_query:
            score = min(score, 60.0)
        best = max(best, score)
    return best


def run_chat_query(db: Session, query: str) -> ChatQueryResponse:
    normalized = normalize_query(query)
    staff = db.scalars(select(StaffMember).where(StaffMember.is_active.is_(True))).all()
    departments = db.scalars(select(Department)).all()
    faculties = db.scalars(select(Faculty)).all()
    guides = db.scalars(select(LocationGuide)).all()
    guide_by_department = {guide.department_id: guide for guide in guides if guide.department_id}

    nlp = build_nlp(staff, departments, faculties)
    doc = nlp(normalized)
    labels = [ent.label_ for ent in doc.ents]
    intent, confidence = detect_intent(normalized, labels)

    if intent in {"person_lookup", "role_lookup", "specialization_lookup", "ambiguous"}:
        if intent == "role_lookup":
            role_query = re.sub(r"^(who is|who s|tell me about)\s+", "", normalized).strip()
            role_query = re.sub(r"^the\s+", "", role_query).strip()
            exact_role_matches = [
                member
                for member in staff
                if member.rank_role
                and (
                    normalize_query(member.rank_role) == role_query
                    or role_query in normalize_query(member.rank_role)
                )
            ]
            if exact_role_matches:
                exact_role_matches.sort(
                    key=lambda member: (
                        0 if normalize_query(member.rank_role or "") == role_query else 1,
                        len(normalize_query(member.rank_role or "")),
                    )
                )
                top_member = exact_role_matches[0]
                response = ChatQueryResponse(
                    intent="role_lookup",
                    confidence="high",
                    answer=build_staff_answer(top_member, guide_by_department.get(top_member.department_id)),
                    matches=[
                        MatchItem(
                            id=member.id,
                            label=member.full_name,
                            kind="staff",
                            score=100.0 if normalize_query(member.rank_role or "") == role_query else 80.0,
                            details=member.rank_role,
                        )
                        for member in exact_role_matches[:5]
                    ],
                    suggested_queries=[],
                )
                db.add(
                    QueryLog(
                        query_text=query,
                        intent=response.intent,
                        confidence=response.confidence,
                        matched_entity_ids=[item.id for item in response.matches],
                    )
                )
                db.commit()
                return response
        candidates: list[tuple[float, StaffMember]] = []
        for member in staff:
            score = _best_staff_score(member, normalized, intent)
            if score >= 55:
                candidates.append((score, member))
        candidates.sort(key=lambda item: item[0], reverse=True)
        if candidates:
            top_score, top_member = candidates[0]
            top_matches = [
                MatchItem(id=member.id, label=member.full_name, kind="staff", score=score, details=member.rank_role)
                for score, member in candidates[:5]
            ]
            if len(candidates) > 1 and top_score - candidates[1][0] < 5:
                response = ChatQueryResponse(
                    intent="ambiguous",
                    confidence="medium",
                    answer="I found several likely matches. Pick one of these staff profiles.",
                    matches=top_matches,
                    suggested_queries=[f"Tell me about {member.full_name}" for _, member in candidates[:3]],
                )
            else:
                response = ChatQueryResponse(
                    intent=intent,
                    confidence=confidence,
                    answer=build_staff_answer(top_member, guide_by_department.get(top_member.department_id)),
                    matches=top_matches,
                    suggested_queries=[],
                )
            db.add(
                QueryLog(
                    query_text=query,
                    intent=response.intent,
                    confidence=response.confidence,
                    matched_entity_ids=[item.id for item in response.matches],
                )
            )
            db.commit()
            return response

    department_candidates: list[tuple[float, Department]] = []
    for department in departments:
        searchable = [department.name, *(department.aliases or []), department.notes or ""]
        score = max(_score(token, normalized) for token in searchable if token)
        if score >= 55:
            department_candidates.append((score, department))
    department_candidates.sort(key=lambda item: item[0], reverse=True)

    if department_candidates:
        top_score, top_department = department_candidates[0]
        faculty = db.get(Faculty, top_department.faculty_id) if top_department.faculty_id else None
        response = ChatQueryResponse(
            intent="location_lookup" if "where" in normalized or "office" in normalized else "department_lookup",
            confidence="high" if top_score >= 80 else "medium",
            answer=build_department_answer(top_department, faculty, guide_by_department.get(top_department.id)),
            matches=[
                MatchItem(id=department.id, label=department.name, kind="department", score=score, details=department.campus)
                for score, department in department_candidates[:5]
            ],
            suggested_queries=[f"Who works in {top_department.name}?", f"Where is {top_department.name}?"],
        )
        db.add(
            QueryLog(
                query_text=query,
                intent=response.intent,
                confidence=response.confidence,
                matched_entity_ids=[item.id for item in response.matches],
            )
        )
        db.commit()
        return response

    faculty_match = db.scalar(
        select(Faculty).where(or_(Faculty.name.ilike(f"%{normalized}%"), Faculty.short_name.ilike(f"%{normalized}%")))
    )
    if faculty_match:
        response = ChatQueryResponse(
            intent="faculty_lookup",
            confidence="medium",
            answer=f"{faculty_match.name} is based on the {faculty_match.campus}.",
            matches=[MatchItem(id=faculty_match.id, label=faculty_match.name, kind="faculty", score=75.0, details=faculty_match.campus)],
            suggested_queries=[f"Where is {faculty_match.short_name or faculty_match.name}?", f"Who is the dean of {faculty_match.short_name or faculty_match.name}?"],
        )
        db.add(QueryLog(query_text=query, intent=response.intent, confidence=response.confidence, matched_entity_ids=[faculty_match.id]))
        db.commit()
        return response

    response = ChatQueryResponse(
        intent="ambiguous",
        confidence="low",
        answer="I could not find a confident match from the current UMaT staff registry.",
        matches=[],
        suggested_queries=[
            "Who is the Vice Chancellor?",
            "Who specializes in cloud computing?",
            "Where is the Department of Geomatic Engineering?",
        ],
    )
    db.add(QueryLog(query_text=query, intent=response.intent, confidence=response.confidence, matched_entity_ids=[]))
    db.commit()
    return response
