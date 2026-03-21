from __future__ import annotations


def build_fact_pack(record: dict[str, object]) -> dict[str, object]:
    facts = dict(record.get("facts", {}))
    return {
        "entity_id": record["entity_id"],
        "entity_type": record["entity_type"],
        "display_name": record["display_name"],
        "aliases": list(record.get("aliases", [])),
        "facts": facts,
        "directions_text": str(facts.get("directions_text") or facts.get("location_guide") or ""),
    }
