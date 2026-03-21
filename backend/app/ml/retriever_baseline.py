from __future__ import annotations

import re
from collections.abc import Iterable

from rapidfuzz import fuzz


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _search_text(record: dict[str, object]) -> str:
    facts = record.get("facts", {})
    parts = [
        str(record.get("display_name", "")),
        " ".join(str(item) for item in record.get("aliases", [])),
    ]
    if isinstance(facts, dict):
        parts.extend(str(value) for value in facts.values() if isinstance(value, (str, int, float)))
        specializations = facts.get("specializations", [])
        if isinstance(specializations, list):
            parts.append(" ".join(str(item) for item in specializations))
    return _normalize(" ".join(parts))


def retrieve_baseline_matches(query: str, dataset: dict[str, list[dict[str, object]]], *, top_k: int = 3) -> list[dict[str, object]]:
    normalized_query = _normalize(query)
    candidates = dataset.get("staff", []) + dataset.get("departments", []) + dataset.get("faculties", [])
    ranked = []
    for record in candidates:
        score = float(fuzz.WRatio(normalized_query, _search_text(record)))
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


def benchmark_retriever_baseline(
    examples: Iterable[dict[str, object]],
    dataset: dict[str, list[dict[str, object]]],
    *,
    top_k: int = 3,
) -> list[dict[str, object]]:
    results = []
    for example in examples:
        matches = retrieve_baseline_matches(str(example["user_message"]), dataset, top_k=top_k)
        results.append(
            {
                "example_key": example.get("example_key"),
                "query": example["user_message"],
                "target_entity_ids": list(example.get("target_entity_ids", [])),
                "matches": matches,
            }
        )
    return results
