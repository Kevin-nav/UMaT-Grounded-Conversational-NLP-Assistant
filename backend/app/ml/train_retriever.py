from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.ml.eval_retriever import aggregate_retriever_metrics
from app.ml.retriever_model import LightweightRetriever, RetrieverArtifact


@dataclass(slots=True)
class RetrieverTrainingConfig:
    project_name: str = "umat_nlp_project"
    output_dir: Path = field(default_factory=lambda: Path("backend/artifacts/umat_nlp_project/retriever"))
    top_k: int = 3


@dataclass(slots=True)
class RetrieverTrainingResult:
    metrics: dict[str, float | int | dict[str, float]]
    artifact_path: Path


def run_retriever_training(
    dataset: dict[str, list[dict[str, object]]],
    examples: list[dict[str, object]],
    *,
    config: RetrieverTrainingConfig | None = None,
) -> RetrieverTrainingResult:
    config = config or RetrieverTrainingConfig()
    records = dataset.get("staff", []) + dataset.get("departments", []) + dataset.get("faculties", [])
    retriever = LightweightRetriever(records)
    results = []
    for example in examples:
        results.append(
            {
                "dialogue_family": example.get("dialogue_family", "unknown"),
                "target_entity_ids": example.get("target_entity_ids", []),
                "matches": retriever.rank(str(example["user_message"]), top_k=config.top_k),
            }
        )
    metrics = aggregate_retriever_metrics(results)
    artifact_path = RetrieverArtifact(project_name=config.project_name, records=records).save(config.output_dir)
    return RetrieverTrainingResult(metrics=metrics, artifact_path=artifact_path)
