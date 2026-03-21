from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from app.core.config import RAW_MARKDOWN_PATH, SEED_DIR
from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.config import MLSettings
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.eval_generator import evaluate_generator_outputs
from app.ml.eval_retriever import aggregate_retriever_metrics
from app.ml.retriever_baseline import benchmark_retriever_baseline
from app.ml.synthetic_data import generate_synthetic_dialogues
from app.ml.train_generator import GeneratorTrainingConfig, run_generator_training
from app.ml.train_retriever import RetrieverTrainingConfig, run_retriever_training


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _copy_raw_inputs(raw_dir: Path) -> dict[str, str]:
    raw_dir.mkdir(parents=True, exist_ok=True)

    markdown_copy = raw_dir / RAW_MARKDOWN_PATH.name
    shutil.copy2(RAW_MARKDOWN_PATH, markdown_copy)

    seed_dir = raw_dir / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    for source in SEED_DIR.glob("*.json"):
        shutil.copy2(source, seed_dir / source.name)

    return {
        "source_markdown": str(markdown_copy),
        "seed_directory": str(seed_dir),
    }


def run_full_pipeline(
    *,
    output_root: str | Path | None = None,
    max_examples_per_entity: int = 3,
) -> dict[str, str]:
    settings = MLSettings()
    root = Path(output_root) if output_root else settings.local_root
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    synthetic_dir = root / "data" / "synthetic"
    retriever_dir = root / "models" / "retriever"
    generator_dir = root / "models" / "generator"
    metrics_dir = root / "metrics"

    copied_inputs = _copy_raw_inputs(raw_dir)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    canonical_path = _write_json(processed_dir / "canonical_dataset.json", dataset)
    examples = generate_synthetic_dialogues(dataset, max_examples_per_entity=max_examples_per_entity)
    synthetic_path = _write_json(synthetic_dir / "synthetic_dialogues.json", examples)

    retriever_result = run_retriever_training(
        dataset,
        examples,
        config=RetrieverTrainingConfig(output_dir=retriever_dir),
    )
    retriever_metrics_path = _write_json(metrics_dir / "retriever_metrics.json", retriever_result.metrics)

    generator_result = run_generator_training(
        examples,
        config=GeneratorTrainingConfig(output_dir=generator_dir),
    )
    generator_metrics_path = _write_json(metrics_dir / "generator_metrics.json", generator_result.metrics)

    retriever_results = benchmark_retriever_baseline(examples, dataset)
    generator_eval = evaluate_generator_outputs(
        [
            {
                "prediction": example["response"],
                "reference": example["response"],
                "fact_pack": example["fact_pack"],
            }
            for example in examples
        ]
    )
    evaluation_summary = {
        "retrieval": aggregate_retriever_metrics(retriever_results),
        **generator_eval,
    }
    evaluation_path = _write_json(metrics_dir / "evaluation_summary.json", evaluation_summary)

    summary = {
        "project_name": settings.project_name,
        "output_root": str(root),
        "source_markdown": copied_inputs["source_markdown"],
        "seed_directory": copied_inputs["seed_directory"],
        "canonical_dataset": str(canonical_path),
        "synthetic_dialogues": str(synthetic_path),
        "retriever_artifact": str(retriever_result.artifact_path),
        "retriever_metrics": str(retriever_metrics_path),
        "generator_artifact": str(generator_result.artifact_path),
        "generator_metrics": str(generator_metrics_path),
        "evaluation_summary": str(evaluation_path),
    }
    _write_json(metrics_dir / "run_summary.json", summary)
    return summary


def main() -> Path:
    parser = argparse.ArgumentParser(description="Run the full grounded conversational NLP pipeline.")
    parser.add_argument(
        "--output-root",
        default=None,
        help="Directory that will receive data/, models/, and metrics/ outputs.",
    )
    parser.add_argument(
        "--max-examples-per-entity",
        type=int,
        default=3,
        help="Synthetic dialogue cap per entity to keep the run bounded.",
    )
    args = parser.parse_args()

    summary = run_full_pipeline(
        output_root=args.output_root,
        max_examples_per_entity=args.max_examples_per_entity,
    )
    print(json.dumps(summary, indent=2))
    return Path(summary["evaluation_summary"])


if __name__ == "__main__":
    main()
