from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.inference import run_ml_chat_query


def test_run_ml_chat_query_returns_experimental_mode_and_grounded_matches() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)
        response = run_ml_chat_query(db, "Tell me about Evans Obu.", dataset=dataset)

    assert response.mode == "ml_experimental"
    assert response.matches
    assert response.matches[0].id == "evans-obu"
