from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.config import MLSettings
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.eval_generator import evaluate_generator_outputs
from app.ml.train_generator import GeneratorTrainingConfig, run_generator_training
from app.ml.train_retriever import RetrieverTrainingConfig, run_retriever_training
from app.ml.synthetic_data import generate_synthetic_dialogues


def run_smoke_pipeline(*, max_examples: int = 20) -> dict[str, str]:
    settings = MLSettings()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    canonical_path = settings.local_root / "canonical_dataset.json"
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(json.dumps(dataset, indent=2), encoding="utf-8")

    examples = generate_synthetic_dialogues(dataset, seed=19, max_examples_per_entity=2)[:max_examples]
    retriever_result = run_retriever_training(dataset, examples, config=RetrieverTrainingConfig(output_dir=settings.local_root / "retriever"))
    generator_result = run_generator_training(examples, config=GeneratorTrainingConfig(output_dir=settings.local_root / "generator"))

    evaluation = evaluate_generator_outputs(
        [
            {"prediction": example["response"], "reference": example["response"], "fact_pack": example["fact_pack"]}
            for example in examples
        ]
    )
    evaluation_path = settings.local_root / "evaluation_summary.json"
    evaluation_path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

    return {
        "project_name": settings.project_name,
        "canonical_dataset": str(canonical_path),
        "retriever_artifact": str(retriever_result.artifact_path),
        "generator_artifact": str(generator_result.artifact_path),
        "evaluation_summary": str(evaluation_path),
    }


def main() -> Path:
    summary = run_smoke_pipeline()
    destination = Path(summary["evaluation_summary"])
    print(json.dumps(summary, indent=2))
    return destination


if __name__ == "__main__":
    main()
