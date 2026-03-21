from __future__ import annotations

from random import Random

from app.ml.templates import (
    DIRECT_LOOKUP_RESPONSE_TEMPLATES,
    DIRECT_LOOKUP_USER_TEMPLATES,
    FOLLOW_UP_LOCATION_RESPONSE_TEMPLATES,
    FOLLOW_UP_LOCATION_USER_TEMPLATES,
    GREETING_RESPONSE_TEMPLATES,
    GREETING_USER_TEMPLATES,
)


CanonicalRecord = dict[str, object]
CanonicalDataset = dict[str, list[CanonicalRecord]]


def _pick(rng: Random, templates: tuple[str, ...], index_hint: int) -> str:
    return templates[index_hint % len(templates)] if templates else ""


def _department_name(dataset: CanonicalDataset, department_id: str | None) -> str:
    if not department_id:
        return "UMaT"
    departments = {item["entity_id"]: item for item in dataset.get("departments", [])}
    department = departments.get(department_id)
    if not department:
        return "UMaT"
    return str(department["display_name"])


def _location_details(dataset: CanonicalDataset, department_id: str | None) -> str:
    guides = dataset.get("location_guides", [])
    for guide in guides:
        facts = guide.get("facts", {})
        if isinstance(facts, dict) and facts.get("department_id") == department_id:
            return str(facts.get("directions_text") or "Please check the department office.")
    return "Please check the department office."


def _build_fact_pack(dataset: CanonicalDataset, record: CanonicalRecord) -> dict[str, object]:
    facts = dict(record.get("facts", {}))
    department_id = facts.get("department_id")
    fact_pack = {
        "entity_id": record["entity_id"],
        "entity_type": record["entity_type"],
        "display_name": record["display_name"],
        "aliases": list(record.get("aliases", [])),
        "department_name": _department_name(dataset, department_id if isinstance(department_id, str) else None),
        "facts": facts,
    }
    fact_pack["directions_text"] = _location_details(dataset, department_id if isinstance(department_id, str) else None)
    return fact_pack


def _direct_lookup_example(dataset: CanonicalDataset, record: CanonicalRecord, index_hint: int) -> dict[str, object]:
    fact_pack = _build_fact_pack(dataset, record)
    name = str(record["display_name"])
    facts = fact_pack["facts"]
    role = str(facts.get("role") or "a staff member")
    department_name = str(fact_pack["department_name"])

    user_message = _pick(Random(index_hint), DIRECT_LOOKUP_USER_TEMPLATES, index_hint).format(name=name)
    response = _pick(Random(index_hint), DIRECT_LOOKUP_RESPONSE_TEMPLATES, index_hint).format(
        name=name,
        role=role,
        department_name=department_name,
    )
    return {
        "dialogue_family": "direct_lookup",
        "history": [],
        "user_message": user_message,
        "target_entity_ids": [record["entity_id"]],
        "fact_pack": fact_pack,
        "response": response,
    }


def _follow_up_location_example(dataset: CanonicalDataset, record: CanonicalRecord, index_hint: int) -> dict[str, object]:
    fact_pack = _build_fact_pack(dataset, record)
    name = str(record["display_name"])
    facts = fact_pack["facts"]
    role = str(facts.get("role") or "a staff member")
    department_name = str(fact_pack["department_name"])
    campus = str(facts.get("campus") or "the relevant UMaT campus")
    directions = str(fact_pack["directions_text"])

    previous_user = _pick(Random(index_hint), DIRECT_LOOKUP_USER_TEMPLATES, index_hint).format(name=name)
    previous_assistant = _pick(Random(index_hint), DIRECT_LOOKUP_RESPONSE_TEMPLATES, index_hint).format(
        name=name,
        role=role,
        department_name=department_name,
    )
    user_message = _pick(Random(index_hint), FOLLOW_UP_LOCATION_USER_TEMPLATES, index_hint).format(pronoun="his")
    response = _pick(Random(index_hint), FOLLOW_UP_LOCATION_RESPONSE_TEMPLATES, index_hint).format(
        name=name,
        campus=campus,
        directions=directions,
    )
    return {
        "dialogue_family": "follow_up_location",
        "history": [
            {"role": "user", "text": previous_user},
            {"role": "assistant", "text": previous_assistant},
        ],
        "user_message": user_message,
        "target_entity_ids": [record["entity_id"]],
        "fact_pack": fact_pack,
        "response": response,
    }


def _greeting_lookup_example(dataset: CanonicalDataset, record: CanonicalRecord, index_hint: int) -> dict[str, object]:
    fact_pack = _build_fact_pack(dataset, record)
    name = str(record["display_name"])
    facts = fact_pack["facts"]
    role = str(facts.get("role") or "a staff member")
    department_name = str(fact_pack["department_name"])
    user_message = _pick(Random(index_hint), GREETING_USER_TEMPLATES, index_hint).format(name=name)
    response = _pick(Random(index_hint), GREETING_RESPONSE_TEMPLATES, index_hint).format(
        name=name,
        role=role,
        department_name=department_name,
    )
    return {
        "dialogue_family": "greeting_lookup",
        "history": [],
        "user_message": user_message,
        "target_entity_ids": [record["entity_id"]],
        "fact_pack": fact_pack,
        "response": response,
    }


def generate_synthetic_dialogues(
    dataset: CanonicalDataset,
    *,
    seed: int = 0,
    max_examples_per_entity: int = 2,
) -> list[dict[str, object]]:
    rng = Random(seed)
    records = [record for record in dataset.get("staff", []) if record.get("entity_type") == "staff"]
    examples: list[dict[str, object]] = []

    for record in records:
        if not bool(dict(record.get("facts", {})).get("is_active", True)):
            continue

        index_hint = rng.randint(0, 10_000)
        examples.append(_direct_lookup_example(dataset, record, index_hint))

        index_hint = rng.randint(0, 10_000)
        examples.append(_greeting_lookup_example(dataset, record, index_hint))

        if max_examples_per_entity > 1:
            index_hint = rng.randint(0, 10_000)
            examples.append(_follow_up_location_example(dataset, record, index_hint))

    return examples
