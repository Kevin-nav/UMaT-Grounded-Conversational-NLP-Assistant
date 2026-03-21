from __future__ import annotations


def _field_coverage(prediction: str, fact_pack: dict[str, object]) -> float:
    facts = dict(fact_pack.get("facts", {}))
    values = [
        str(fact_pack.get("display_name", "")),
        str(facts.get("campus", "")),
        str(fact_pack.get("directions_text", "")),
    ]
    populated = [value for value in values if value]
    if not populated:
        return 0.0
    hits = sum(1 for value in populated if value in prediction)
    return hits / len(populated)


def evaluate_generator_outputs(predictions: list[dict[str, object]]) -> dict[str, dict[str, float | int]]:
    if not predictions:
        return {"generation": {"example_count": 0, "factuality_score": 0.0, "field_coverage": 0.0}}

    total_factuality = 0.0
    total_coverage = 0.0
    for item in predictions:
        prediction = str(item.get("prediction", ""))
        reference = str(item.get("reference", ""))
        fact_pack = dict(item.get("fact_pack", {}))
        total_factuality += 1.0 if prediction == reference or _field_coverage(prediction, fact_pack) > 0 else 0.0
        total_coverage += _field_coverage(prediction, fact_pack)

    count = len(predictions)
    return {
        "generation": {
            "example_count": count,
            "factuality_score": total_factuality / count,
            "field_coverage": total_coverage / count,
        }
    }
