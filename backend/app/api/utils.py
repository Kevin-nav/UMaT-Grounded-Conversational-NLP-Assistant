from __future__ import annotations

from typing import TypeVar


T = TypeVar("T")


def split_lines(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.splitlines() if item.strip()]


def join_lines(values: list[str] | None) -> str | None:
    if values is None:
        return None
    clean = [value.strip() for value in values if value and value.strip()]
    return "\n".join(clean)
