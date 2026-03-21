from __future__ import annotations

from collections.abc import Iterable


def _example_key(example: dict[str, object]) -> str:
    targets = ",".join(str(item) for item in example.get("target_entity_ids", []))
    return f"{example.get('dialogue_family')}|{example.get('user_message')}|{targets}"


def build_training_splits(
    examples: Iterable[dict[str, object]],
    *,
    validation_families: set[str] | None = None,
    test_families: set[str] | None = None,
) -> dict[str, list[dict[str, object]]]:
    validation_families = validation_families or set()
    test_families = test_families or set()

    splits = {"train": [], "validation": [], "test": []}
    seen_keys: set[str] = set()

    for example in examples:
        enriched = dict(example)
        enriched["example_key"] = _example_key(example)
        if enriched["example_key"] in seen_keys:
            continue
        seen_keys.add(enriched["example_key"])

        family = str(enriched.get("dialogue_family", ""))
        if family in validation_families:
            splits["validation"].append(enriched)
        elif family in test_families:
            splits["test"].append(enriched)
        else:
            splits["train"].append(enriched)

    return splits
