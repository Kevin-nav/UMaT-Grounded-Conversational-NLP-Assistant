from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


def _tokenize(text: str) -> set[str]:
    return {token for token in re.sub(r"[^a-z0-9\s]", " ", text.lower()).split() if token}


@dataclass(slots=True)
class RetrieverArtifact:
    project_name: str
    records: list[dict[str, object]]

    def save(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = output_dir / "retriever_artifact.json"
        artifact_path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return artifact_path


class LightweightRetriever:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records

    def rank(self, query: str, *, top_k: int = 3) -> list[dict[str, object]]:
        query_tokens = _tokenize(query)
        ranked = []
        for record in self.records:
            haystack = " ".join(
                [
                    str(record.get("display_name", "")),
                    " ".join(str(item) for item in record.get("aliases", [])),
                    json.dumps(record.get("facts", {}), sort_keys=True),
                ]
            )
            record_tokens = _tokenize(haystack)
            overlap = len(query_tokens & record_tokens)
            score = overlap / max(len(query_tokens), 1)
            ranked.append(
                {
                    "entity_id": record["entity_id"],
                    "entity_type": record["entity_type"],
                    "display_name": record["display_name"],
                    "score": score,
                }
            )
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:top_k]
