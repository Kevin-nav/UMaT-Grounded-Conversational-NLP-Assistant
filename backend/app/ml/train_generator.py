from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.ml.generator_model import GeneratorArtifact, LightweightGenerator


@dataclass(slots=True)
class GeneratorTrainingConfig:
    project_name: str = "umat_nlp_project"
    output_dir: Path = field(default_factory=lambda: Path("backend/artifacts/umat_nlp_project/generator"))


@dataclass(slots=True)
class GeneratorTrainingResult:
    metrics: dict[str, float]
    artifact_path: Path


def prepare_generator_examples(examples: list[dict[str, object]]) -> list[dict[str, str]]:
    prepared = []
    for example in examples:
        history = " ".join(f"{turn['role']}: {turn['text']}" for turn in example.get("history", []))
        fact_pack = example.get("fact_pack", {})
        prepared.append(
            {
                "input_text": f"{history}\nuser: {example['user_message']}\nfacts: {fact_pack}",
                "target_text": str(example["response"]),
            }
        )
    return prepared


def run_generator_training(
    examples: list[dict[str, object]],
    *,
    config: GeneratorTrainingConfig | None = None,
) -> GeneratorTrainingResult:
    config = config or GeneratorTrainingConfig()
    prepared = prepare_generator_examples(examples)
    generator = LightweightGenerator()
    exact_matches = 0
    for example in examples:
        if generator.generate(example) == example["response"]:
            exact_matches += 1

    train_loss = max(0.0, 1.0 - (exact_matches / max(len(examples), 1)))
    validation_score = 1.0 - train_loss
    artifact_path = GeneratorArtifact(project_name=config.project_name, examples=prepared).save(config.output_dir)
    return GeneratorTrainingResult(
        metrics={"train_loss": train_loss, "validation_score": validation_score},
        artifact_path=artifact_path,
    )
