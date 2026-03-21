from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues


def main(output_path: str | None = None) -> Path:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    payload = generate_synthetic_dialogues(dataset)
    destination = Path(output_path) if output_path else Path("backend/artifacts/umat_nlp_project/synthetic_dialogues.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


if __name__ == "__main__":
    saved_to = main()
    print(f"Synthetic dialogues exported to {saved_to}")
