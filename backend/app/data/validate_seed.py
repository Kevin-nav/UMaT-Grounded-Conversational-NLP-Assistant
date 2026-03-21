from __future__ import annotations

import json
from pathlib import Path

from app.core.config import SEED_DIR


REQUIRED_FILES = {
    "faculties": {"id", "name"},
    "departments": {"id", "name"},
    "staff": {"id", "full_name"},
    "location_guides": {"id", "directions_text"},
}


class SeedValidationError(ValueError):
    pass


def load_seed_file(name: str, seed_dir: Path = SEED_DIR) -> list[dict]:
    path = seed_dir / f"{name}.json"
    if not path.exists():
        raise SeedValidationError(f"Missing seed file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_seed(seed_dir: Path = SEED_DIR) -> None:
    data = {name: load_seed_file(name, seed_dir) for name in REQUIRED_FILES}
    faculty_ids = {item["id"] for item in data["faculties"]}
    department_ids = {item["id"] for item in data["departments"]}

    for file_name, required_fields in REQUIRED_FILES.items():
        for index, record in enumerate(data[file_name]):
            missing = sorted(field for field in required_fields if not record.get(field))
            if missing:
                raise SeedValidationError(f"{file_name}[{index}] missing required fields: {', '.join(missing)}")

    for record in data["departments"]:
        faculty_id = record.get("faculty_id")
        if faculty_id and faculty_id not in faculty_ids:
            raise SeedValidationError(f"Department {record['id']} references missing faculty {faculty_id}")

    for record in data["staff"]:
        faculty_id = record.get("faculty_id")
        department_id = record.get("department_id")
        if faculty_id and faculty_id not in faculty_ids:
            raise SeedValidationError(f"Staff {record['id']} references missing faculty {faculty_id}")
        if department_id and department_id not in department_ids:
            raise SeedValidationError(f"Staff {record['id']} references missing department {department_id}")

    for record in data["location_guides"]:
        faculty_id = record.get("faculty_id")
        department_id = record.get("department_id")
        if faculty_id and faculty_id not in faculty_ids:
            raise SeedValidationError(f"Location guide {record['id']} references missing faculty {faculty_id}")
        if department_id and department_id not in department_ids:
            raise SeedValidationError(f"Location guide {record['id']} references missing department {department_id}")

