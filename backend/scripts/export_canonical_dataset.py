from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset


def main(output_path: str | None = None) -> Path:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        payload = export_canonical_dataset(db)

    destination = Path(output_path) if output_path else Path("backend/artifacts/umat_nlp_project/canonical_dataset.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


if __name__ == "__main__":
    saved_to = main()
    print(f"Canonical dataset exported to {saved_to}")
