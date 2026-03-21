from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import BACKEND_DIR, ROOT_DIR


def _default_drive_root() -> str:
    return "MyDrive/umat_nlp_project"


@dataclass(slots=True)
class MLSettings:
    project_name: str = "umat_nlp_project"
    local_root: Path = field(default_factory=lambda: BACKEND_DIR / "artifacts" / "umat_nlp_project")
    drive_root: str = field(default_factory=_default_drive_root)
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    synthetic_data_dir: str = "data/synthetic"
    retriever_model_dir: str = "models/retriever"
    generator_model_dir: str = "models/generator"
    metrics_dir: str = "metrics"
    notebooks_dir: Path = field(default_factory=lambda: ROOT_DIR / "backend" / "notebooks")

