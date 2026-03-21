from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import RAW_MARKDOWN_PATH, SEED_DIR, get_settings
from app.core.security import get_password_hash
from app.data.extract_markdown import extract_dataset, write_seed_files
from app.data.validate_seed import validate_seed
from app.db.models import AdminUser, Department, Faculty, LocationGuide, StaffMember


def _load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_seed_files() -> None:
    dataset = extract_dataset(RAW_MARKDOWN_PATH)
    write_seed_files(dataset, SEED_DIR)
    validate_seed(SEED_DIR)


def ensure_bootstrap_users(db: Session) -> None:
    settings = get_settings()
    defaults = [
        {
            "full_name": settings.bootstrap_admin_name,
            "email": settings.bootstrap_admin_email,
            "password": settings.bootstrap_admin_password,
            "role": "super_admin",
        },
        {
            "full_name": "UMaT Editor",
            "email": settings.bootstrap_editor_email,
            "password": settings.bootstrap_editor_password,
            "role": "editor",
        },
        {
            "full_name": "UMaT Viewer",
            "email": settings.bootstrap_viewer_email,
            "password": settings.bootstrap_viewer_password,
            "role": "viewer",
        },
    ]
    changed = False
    for user in defaults:
        exists = db.scalar(select(AdminUser.id).where(AdminUser.email == user["email"]))
        if exists:
            continue
        db.add(
            AdminUser(
                full_name=user["full_name"],
                email=user["email"],
                password_hash=get_password_hash(user["password"]),
                role=user["role"],
                is_active=True,
            )
        )
        changed = True
    if changed:
        db.commit()


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(Faculty.id).limit(1)):
        ensure_bootstrap_users(db)
        return

    generate_seed_files()
    for record in _load_json(SEED_DIR / "faculties.json"):
        db.add(Faculty(**record))
    for record in _load_json(SEED_DIR / "departments.json"):
        db.add(Department(**record))
    for record in _load_json(SEED_DIR / "staff.json"):
        db.add(StaffMember(**record))
    for record in _load_json(SEED_DIR / "location_guides.json"):
        db.add(LocationGuide(**record))
    db.commit()
    ensure_bootstrap_users(db)

