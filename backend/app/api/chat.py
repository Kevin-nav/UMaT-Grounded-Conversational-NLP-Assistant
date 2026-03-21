from fastapi import APIRouter

from app.api.dependencies import DbDep
from app.core.config import get_settings
from app.ml.inference import run_ml_chat_query
from app.nlp.retrieval import run_chat_query
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
def query_chat(payload: ChatQueryRequest, db: DbDep) -> ChatQueryResponse:
    settings = get_settings()
    if settings.ml_experimental_enabled:
        return run_ml_chat_query(db, payload.query)
    return run_chat_query(db, payload.query)
