from __future__ import annotations

from collections import defaultdict


def aggregate_retriever_metrics(results: list[dict[str, object]]) -> dict[str, float | int | dict[str, float]]:
    if not results:
        return {"example_count": 0, "top_1_accuracy": 0.0, "top_3_accuracy": 0.0, "mrr": 0.0, "by_family": {}}

    top_1_hits = 0
    top_3_hits = 0
    reciprocal_rank_total = 0.0
    by_family_counts: dict[str, list[float]] = defaultdict(list)

    for result in results:
        targets = set(result.get("target_entity_ids", []))
        matches = list(result.get("matches", []))
        family = str(result.get("dialogue_family", "unknown"))
        hit_rank = 0

        for index, match in enumerate(matches, start=1):
            if match.get("entity_id") in targets:
                hit_rank = index
                break

        if hit_rank == 1:
            top_1_hits += 1
        if hit_rank and hit_rank <= 3:
            top_3_hits += 1
        if hit_rank:
            reciprocal_rank_total += 1.0 / hit_rank
        by_family_counts[family].append(1.0 if hit_rank == 1 else 0.0)

    example_count = len(results)
    return {
        "example_count": example_count,
        "top_1_accuracy": top_1_hits / example_count,
        "top_3_accuracy": top_3_hits / example_count,
        "mrr": reciprocal_rank_total / example_count,
        "by_family": {family: sum(values) / len(values) for family, values in by_family_counts.items()},
    }
