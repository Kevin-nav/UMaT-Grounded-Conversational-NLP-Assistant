from __future__ import annotations

from collections import Counter


INTENT_KEYWORDS = {
    "location_lookup": {"where", "locate", "location", "office", "find"},
    "role_lookup": {"who is", "vice chancellor", "dean", "registrar", "head"},
    "specialization_lookup": {"specializes", "specialisation", "specialization", "teaches", "research", "cloud", "gis"},
    "department_lookup": {"department", "faculty", "school"},
    "person_lookup": {"who", "lecturer", "staff", "profile"},
}


def detect_intent(normalized_query: str, entity_labels: list[str]) -> tuple[str, str]:
    explicit_role_terms = ("vice chancellor", "pro vice chancellor", "dean", "registrar", "chancellor", "head of department")
    if any(term in normalized_query for term in explicit_role_terms):
        return "role_lookup", "high"

    counter = Counter()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized_query for keyword in keywords):
            counter[intent] += 2
    for label in entity_labels:
        if label == "PERSON":
            counter["person_lookup"] += 2
        elif label == "ROLE":
            counter["role_lookup"] += 2
        elif label == "DEPARTMENT":
            counter["department_lookup"] += 2
        elif label == "FACULTY":
            counter["faculty_lookup"] += 2
        elif label == "SPECIALIZATION":
            counter["specialization_lookup"] += 2
    if not counter:
        return "ambiguous", "low"
    intent, score = counter.most_common(1)[0]
    confidence = "high" if score >= 4 else "medium"
    return intent, confidence
