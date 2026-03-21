import re


TITLE_MAP = {
    "vc": "vice chancellor",
    "hod": "head of department",
    "dept": "department",
    "fcams": "faculty of computing and mathematical sciences",
}


def normalize_query(query: str) -> str:
    normalized = query.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    for source, target in TITLE_MAP.items():
        normalized = re.sub(rf"\b{re.escape(source)}\b", target, normalized)
    return normalized.strip()

