from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.splits import build_training_splits
from app.ml.synthetic_data import generate_synthetic_dialogues


def main(output_path: str | None = None) -> Path:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset)
    splits = build_training_splits(
        examples,
        validation_families={"follow_up_location"},
        test_families={"direct_lookup"},
    )
    destination = Path(output_path) if output_path else Path("backend/artifacts/umat_nlp_project/training_splits.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(splits, indent=2), encoding="utf-8")
    return destination


if __name__ == "__main__":
    saved_to = main()
    print(f"Training splits exported to {saved_to}")
