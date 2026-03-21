from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import RAW_MARKDOWN_PATH, SEED_DIR


TITLE_PATTERN = re.compile(r"^(Prof\.|Dr\.|Mr\.|Mrs\.|Ms\.|His Excellency)\s+", re.IGNORECASE)
HEADING_PATTERN = re.compile(r"^(#{2,3})\s+\*\*(.+?)\*\*$", re.MULTILINE)
PLAIN_BOLD_SECTION_PATTERN = re.compile(r"^\*\*(\d+\\\.\s+.+?)\*\*$", re.MULTILINE)
TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$", re.MULTILINE)
PAIR_PATTERN = re.compile(r"^\*\s+\*\*(?P<left>[^*]+):\*\*\s+\*\*(?P<right>[^*]+)\*\*(?P<rest>.*)$", re.MULTILINE)
FOCUS_DEPARTMENT_PATTERN = re.compile(r"^\*\s+\*\*(Department of [^:*]+):\*\*\s+(?P<focus>.+)$", re.MULTILINE)


@dataclass(slots=True)
class Section:
    heading_level: int
    title: str
    body: str
    start: int


FACULTY_MAP = {
    "Faculty of Mining and Minerals Technology (FMMT)": {"id": "fmmt", "short_name": "FMMT", "campus": "Tarkwa Campus"},
    "Faculty of Geosciences and Environmental Studies (FGES)": {"id": "fges", "short_name": "FGES", "campus": "Tarkwa Campus"},
    "Faculty of Engineering (FoE)": {"id": "foe", "short_name": "FoE", "campus": "Tarkwa Campus"},
    "School of Railways and Infrastructure Development (SRID)": {"id": "srid", "short_name": "SRID", "campus": "Essikado Campus"},
    "Faculty of Integrated Management Science (FIMS)": {"id": "fims", "short_name": "FIMS", "campus": "Tarkwa Campus"},
    "Faculty of Computing and Mathematical Sciences (FCaMS)": {"id": "fcams", "short_name": "FCaMS", "campus": "Tarkwa Campus"},
    "School of Petroleum Studies (SPeTs)": {"id": "spets", "short_name": "SPeTs", "campus": "Tarkwa Campus"},
}

SPECIAL_DEPARTMENTS = {
    "School of Railways and Infrastructure Development (SRID)": [
        "Department of Geomatic and Civil Engineering",
        "Department of Geological and Environmental Engineering",
        "Department of Electrical and Mechanical Engineering",
    ],
    "School of Petroleum Studies (SPeTs)": [
        "Department of Petroleum and Natural Gas Engineering",
        "Department of Petroleum Geosciences and Engineering",
        "Department of Chemical and Petrochemical Engineering",
    ],
}

NON_FACULTY_SECTION_TITLES = {
    "The Chancellery and Vice-Chancellery",
    "Central Administrative Registry",
    "Works and Physical Development",
    "Information Technology (IT) Services",
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.replace("\\.", ".").replace("**", "")
    return re.sub(r"\s+", " ", cleaned).strip(" .")


def normalize_heading_title(title: str) -> str:
    normalized = clean_text(title) or ""
    normalized = re.sub(r"^\d+(?:\.\d+)*\s*", "", normalized)
    normalized = re.sub(r"^[^A-Za-z]+", "", normalized)
    return normalized


def match_faculty(title: str) -> tuple[str, dict[str, Any]] | tuple[None, None]:
    for faculty_name, config in FACULTY_MAP.items():
        plain_name = re.sub(r"\s+\([^)]+\)$", "", faculty_name)
        if title == faculty_name or title == plain_name or plain_name in title:
            return faculty_name, config
    return None, None


def split_name_and_title(name: str) -> tuple[str | None, str]:
    match = TITLE_PATTERN.match(name.strip())
    if not match:
        return None, clean_text(name) or name
    return clean_text(match.group(1)), clean_text(name[match.end() :]) or name


def looks_like_name(value: str) -> bool:
    return bool(TITLE_PATTERN.match(value.strip()))


def parse_sections(markdown: str) -> list[Section]:
    matches = list(HEADING_PATTERN.finditer(markdown)) + list(PLAIN_BOLD_SECTION_PATTERN.finditer(markdown))
    matches.sort(key=lambda item: item.start())
    sections: list[Section] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        if match.re is HEADING_PATTERN:
            title = normalize_heading_title(match.group(2))
            level = len(match.group(1))
        else:
            title = normalize_heading_title(match.group(1))
            level = 2
        sections.append(Section(heading_level=level, title=title, body=markdown[start:end].strip(), start=match.start()))
    return sections


def extract_faculties(markdown: str) -> list[dict[str, Any]]:
    faculties: list[dict[str, Any]] = []
    for section in parse_sections(markdown):
        faculty_name, config = match_faculty(section.title)
        if not config:
            continue
        faculties.append(
            {
                "id": config["id"],
                "name": faculty_name,
                "short_name": config["short_name"],
                "campus": config["campus"],
                "description": clean_text(section.body.split("\n\n", 1)[0]),
            }
        )
    return faculties


def faculty_lookup(faculties: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for faculty in faculties:
        lookup[faculty["name"]] = faculty
        lookup[re.sub(r"\s+\([^)]+\)$", "", faculty["name"])] = faculty
    return lookup


def build_department_guide(department_name: str, faculty: dict[str, Any] | None) -> str:
    campus = faculty["campus"] if faculty else "Tarkwa Campus"
    faculty_name = faculty["name"] if faculty else "UMaT"
    return (
        f"Visit the departmental office for {department_name} at the {campus}. "
        f"If you are unsure of the exact building, start at the {faculty_name} administrative office."
    )


def extract_departments(markdown: str, faculties: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections = parse_sections(markdown)
    lookup = faculty_lookup(faculties)
    current_faculty: dict[str, Any] | None = None
    departments: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for section in sections:
        faculty_name, faculty_config = match_faculty(section.title)
        if faculty_name and faculty_config:
            current_faculty = lookup[faculty_name]
            continue
        if section.heading_level == 3 and section.title.startswith("Department of "):
            department_id = slugify(section.title)
            if department_id in seen_ids:
                continue
            departments.append(
                {
                    "id": department_id,
                    "faculty_id": current_faculty["id"] if current_faculty else None,
                    "name": section.title,
                    "aliases": [section.title.replace("Department of ", "").strip()],
                    "campus": current_faculty["campus"] if current_faculty else None,
                    "location_guide": build_department_guide(section.title, current_faculty),
                    "notes": clean_text(section.body.split("\n\n", 1)[0]),
                }
            )
            seen_ids.add(department_id)

    for faculty_name, department_names in SPECIAL_DEPARTMENTS.items():
        faculty = lookup.get(faculty_name)
        if not faculty:
            continue
        for department_name in department_names:
            department_id = slugify(department_name)
            if department_id in seen_ids:
                continue
            focus_match = next(
                (
                    match.group("focus")
                    for match in FOCUS_DEPARTMENT_PATTERN.finditer(markdown)
                    if normalize_heading_title(match.group(1)) == department_name
                ),
                None,
            )
            departments.append(
                {
                    "id": department_id,
                    "faculty_id": faculty["id"],
                    "name": department_name,
                    "aliases": [department_name.replace("Department of ", "").strip()],
                    "campus": faculty["campus"],
                    "location_guide": build_department_guide(department_name, faculty),
                    "notes": clean_text(focus_match),
                }
            )
            seen_ids.add(department_id)
    return departments


def extract_table_records(section_title: str, section_body: str) -> list[dict[str, str]]:
    rows = [match.group(1) for match in TABLE_ROW_PATTERN.finditer(section_body)]
    parsed_rows: list[list[str]] = []
    for row in rows:
        cols = [clean_text(cell) or "" for cell in row.split("|")]
        if any(col.startswith(":----") for col in cols):
            continue
        parsed_rows.append(cols)
    if len(parsed_rows) < 2:
        return []
    headers = parsed_rows[0]
    records: list[dict[str, str]] = []
    for row in parsed_rows[1:]:
        if len(row) != len(headers):
            continue
        record = {headers[idx].lower().replace("/", "_").replace(" ", "_"): row[idx] for idx in range(len(headers))}
        if any(record.values()):
            record["__section__"] = section_title
            records.append(record)
    return records


def extract_specializations(text: str | None) -> list[str]:
    if not text:
        return []
    candidates: list[str] = []
    for item in re.findall(r"\*\*([^*]+)\*\*", text):
        normalized = clean_text(item)
        if not normalized:
            continue
        if normalized.startswith(("Prof", "Dr", "Mr", "Mrs", "Ms", "His Excellency")):
            continue
        if any(token in normalized for token in ("PhD", "MSc", "MBA", "BA", "BSc", "MPhil", "Dip", "FWAIMM")):
            continue
        candidates.append(normalized)
    for pattern in (
        r"(?:specializes in|focuses on|research interests? (?:are|include)|areas of expertise are|include[s]?|covers)\s+([^.;]+)",
        r"(?:background in|work likely covers)\s+([^.;]+)",
    ):
        for match in re.finditer(pattern, text, re.IGNORECASE):
            for part in re.split(r",| and ", match.group(1)):
                normalized = clean_text(part)
                if normalized and len(normalized) > 3:
                    candidates.append(normalized)
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped[:8]


def resolve_department_id(name: str | None, departments: list[dict[str, Any]]) -> str | None:
    if not name:
        return None
    department_name = clean_text(name)
    if not department_name:
        return None
    for department in departments:
        if department["name"] == department_name:
            return department["id"]
    if not department_name.startswith("Department of "):
        canonical = f"Department of {department_name}"
        for department in departments:
            if department["name"] == canonical:
                return department["id"]
    return None


def upsert_staff(staff_by_id: dict[str, dict[str, Any]], incoming: dict[str, Any]) -> None:
    existing = staff_by_id.get(incoming["id"])
    if not existing:
        staff_by_id[incoming["id"]] = incoming
        return
    for field in ("rank_role", "faculty_id", "department_id", "campus"):
        if not existing.get(field) and incoming.get(field):
            existing[field] = incoming[field]
    if incoming.get("bio") and len(incoming["bio"] or "") > len(existing.get("bio") or ""):
        existing["bio"] = incoming["bio"]
    existing["aliases"] = sorted({*(existing.get("aliases") or []), *(incoming.get("aliases") or [])})
    existing["specializations"] = sorted({*(existing.get("specializations") or []), *(incoming.get("specializations") or [])})
    if incoming.get("source_notes"):
        notes = [existing.get("source_notes"), incoming["source_notes"]]
        existing["source_notes"] = " | ".join(note for note in notes if note)


def extract_staff(markdown: str, faculties: list[dict[str, Any]], departments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections = parse_sections(markdown)
    faculty_by_name = faculty_lookup(faculties)
    current_faculty: dict[str, Any] | None = None
    current_department: dict[str, Any] | None = None
    staff_by_id: dict[str, dict[str, Any]] = {}

    for section in sections:
        faculty_name, _ = match_faculty(section.title)
        if faculty_name:
            current_faculty = faculty_by_name[faculty_name]
            current_department = None
        elif section.title in NON_FACULTY_SECTION_TITLES:
            current_faculty = None
            current_department = None
        elif section.heading_level == 3 and section.title.startswith("Department of "):
            department_id = resolve_department_id(section.title, departments)
            current_department = next((item for item in departments if item["id"] == department_id), None)

        for record in extract_table_records(section.title, section.body):
            name = record.get("name") or record.get("portfolio") or ""
            title, clean_name = split_name_and_title(name)
            if not clean_name:
                continue
            role = record.get("rank_role") or record.get("role_portfolio") or record.get("role") or record.get("portfolio")
            profile = " ".join(
                value
                for key, value in record.items()
                if key not in {"name", "rank_role", "role", "role_portfolio", "portfolio", "__section__"} and value
            )
            upsert_staff(
                staff_by_id,
                {
                    "id": slugify(clean_name),
                    "full_name": clean_name,
                    "title": title,
                    "rank_role": clean_text(role),
                    "faculty_id": current_faculty["id"] if current_faculty else None,
                    "department_id": current_department["id"] if current_department else None,
                    "campus": current_department["campus"] if current_department else (current_faculty["campus"] if current_faculty else None),
                    "specializations": extract_specializations(profile),
                    "bio": clean_text(profile),
                    "aliases": [name] if name and name != clean_name else [],
                    "source_section": section.title,
                    "source_notes": None,
                    "is_active": True,
                },
            )

        for match in PAIR_PATTERN.finditer(section.body):
            left = clean_text(match.group("left")) or ""
            right = clean_text(match.group("right")) or ""
            raw_name, role = (left, right) if looks_like_name(left) else (right, left)
            title, clean_name = split_name_and_title(raw_name)
            if not clean_name:
                continue
            rest = clean_text(match.group("rest"))
            upsert_staff(
                staff_by_id,
                {
                    "id": slugify(clean_name),
                    "full_name": clean_name,
                    "title": title,
                    "rank_role": role,
                    "faculty_id": current_faculty["id"] if current_faculty else None,
                    "department_id": current_department["id"] if current_department else None,
                    "campus": current_department["campus"] if current_department else (current_faculty["campus"] if current_faculty else None),
                    "specializations": extract_specializations(rest),
                    "bio": rest,
                    "aliases": [raw_name],
                    "source_section": section.title,
                    "source_notes": rest,
                    "is_active": True,
                },
            )

    return list(staff_by_id.values())


def extract_location_guides(faculties: list[dict[str, Any]], departments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    guides: list[dict[str, Any]] = []
    for faculty in faculties:
        guides.append(
            {
                "id": f"guide-{faculty['id']}",
                "faculty_id": faculty["id"],
                "department_id": None,
                "campus": faculty["campus"],
                "directions_text": (
                    f"The {faculty['name']} is based on the {faculty['campus']}. "
                    f"Start at the faculty office or central reception for directions to individual departments."
                ),
            }
        )
    for department in departments:
        guides.append(
            {
                "id": f"guide-{department['id']}",
                "faculty_id": department["faculty_id"],
                "department_id": department["id"],
                "campus": department["campus"],
                "directions_text": department["location_guide"]
                or f"Go to the {department['campus']} and ask for the {department['name']} office.",
            }
        )
    return guides


def extract_dataset(markdown_path: Path = RAW_MARKDOWN_PATH) -> dict[str, list[dict[str, Any]]]:
    markdown = markdown_path.read_text(encoding="utf-8", errors="replace")
    faculties = extract_faculties(markdown)
    departments = extract_departments(markdown, faculties)
    staff = extract_staff(markdown, faculties, departments)
    location_guides = extract_location_guides(faculties, departments)
    return {"faculties": faculties, "departments": departments, "staff": staff, "location_guides": location_guides}


def write_seed_files(dataset: dict[str, list[dict[str, Any]]], output_dir: Path = SEED_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, records in dataset.items():
        (output_dir / f"{key}.json").write_text(json.dumps(records, indent=2, ensure_ascii=True), encoding="utf-8")


def main() -> None:
    write_seed_files(extract_dataset())


if __name__ == "__main__":
    main()
