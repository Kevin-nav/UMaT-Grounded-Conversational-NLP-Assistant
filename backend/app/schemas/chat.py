from __future__ import annotations

from pydantic import BaseModel, Field


class MatchItem(BaseModel):
    id: str
    label: str
    kind: str
    score: float
    details: str | None = None


class ChatQueryRequest(BaseModel):
    query: str


class ChatQueryResponse(BaseModel):
    intent: str
    confidence: str
    answer: str
    matches: list[MatchItem] = Field(default_factory=list)
    suggested_queries: list[str] = Field(default_factory=list)
    mode: str = "rule_based"
