from __future__ import annotations

from sqlalchemy.orm import Session

from app.ml.dataset_builder import export_canonical_dataset
from app.ml.fact_pack import build_fact_pack
from app.ml.generator_model import LightweightGenerator
from app.ml.retriever_model import LightweightRetriever
from app.schemas.chat import ChatQueryResponse, MatchItem


def run_ml_chat_query(
    db: Session,
    query: str,
    *,
    dataset: dict[str, list[dict[str, object]]] | None = None,
) -> ChatQueryResponse:
    dataset = dataset or export_canonical_dataset(db)
    records = dataset.get("staff", []) + dataset.get("departments", []) + dataset.get("faculties", [])
    retriever = LightweightRetriever(records)
    generator = LightweightGenerator()
    ranked = retriever.rank(query, top_k=5)

    if not ranked:
        return ChatQueryResponse(
            intent="ambiguous",
            confidence="low",
            answer="I could not find a grounded match in the current UMaT dataset.",
            matches=[],
            suggested_queries=["Tell me about Evans Obu."],
            mode="ml_experimental",
        )

    top_match = ranked[0]
    record = next(item for item in records if item["entity_id"] == top_match["entity_id"])
    fact_pack = build_fact_pack(record)
    answer = generator.generate({"user_message": query, "fact_pack": fact_pack})

    return ChatQueryResponse(
        intent=f"{record['entity_type']}_lookup",
        confidence="medium" if top_match["score"] < 1 else "high",
        answer=answer,
        matches=[
            MatchItem(
                id=str(match["entity_id"]),
                label=str(match["display_name"]),
                kind=str(match["entity_type"]),
                score=float(match["score"]),
            )
            for match in ranked
        ],
        suggested_queries=[],
        mode="ml_experimental",
    )
