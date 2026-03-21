from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class GeneratorArtifact:
    project_name: str
    examples: list[dict[str, str]]

    def save(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = output_dir / "generator_artifact.json"
        artifact_path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return artifact_path


class LightweightGenerator:
    def generate(self, example: dict[str, object]) -> str:
        fact_pack = dict(example.get("fact_pack", {}))
        facts = dict(fact_pack.get("facts", {}))
        name = str(fact_pack.get("display_name", "This staff member"))
        role = str(facts.get("role") or "a staff member")
        campus = str(facts.get("campus") or "the relevant UMaT campus")
        directions = str(fact_pack.get("directions_text") or "")
        message = str(example.get("user_message", "")).lower()

        if "where" in message or "office" in message or "locat" in message:
            suffix = f" {directions}".strip()
            return f"{name} is based at {campus}.{(' ' + suffix) if suffix else ''}".strip()
        return f"{name} is {role}."
