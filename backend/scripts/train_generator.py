from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues
from app.ml.train_generator import GeneratorTrainingConfig, run_generator_training


def main(output_dir: str | None = None) -> Path:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset)
    config = GeneratorTrainingConfig(output_dir=Path(output_dir) if output_dir else Path("backend/artifacts/umat_nlp_project/generator"))
    result = run_generator_training(examples, config=config)
    metrics_path = result.artifact_path.parent / "metrics.json"
    metrics_path.write_text(json.dumps(result.metrics, indent=2), encoding="utf-8")
    return metrics_path


if __name__ == "__main__":
    saved_to = main()
    print(f"Generator metrics written to {saved_to}")
