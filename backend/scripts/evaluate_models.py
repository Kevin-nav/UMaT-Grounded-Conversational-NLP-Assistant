from __future__ import annotations

import json
from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.eval_generator import evaluate_generator_outputs
from app.ml.eval_retriever import aggregate_retriever_metrics
from app.ml.retriever_baseline import benchmark_retriever_baseline
from app.ml.synthetic_data import generate_synthetic_dialogues


def main(output_path: str | None = None) -> Path:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset)
    retriever_results = benchmark_retriever_baseline(examples, dataset)
    generation_inputs = [
        {"prediction": example["response"], "reference": example["response"], "fact_pack": example["fact_pack"]}
        for example in examples
    ]
    payload = {
        "retrieval": aggregate_retriever_metrics(retriever_results),
        **evaluate_generator_outputs(generation_inputs),
    }
    destination = Path(output_path) if output_path else Path("backend/artifacts/umat_nlp_project/evaluation_summary.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


if __name__ == "__main__":
    saved_to = main()
    print(f"Evaluation summary written to {saved_to}")
