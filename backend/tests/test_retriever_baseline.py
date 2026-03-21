from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.eval_retriever import aggregate_retriever_metrics
from app.ml.retriever_baseline import benchmark_retriever_baseline, retrieve_baseline_matches
from app.ml.synthetic_data import generate_synthetic_dialogues


def test_retriever_baseline_returns_ranked_matches_and_metrics() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset, seed=5, max_examples_per_entity=2)
    single_result = retrieve_baseline_matches(examples[0]["user_message"], dataset, top_k=3)

    assert len(single_result) == 3
    assert {"entity_id", "score"} <= set(single_result[0])

    benchmark = benchmark_retriever_baseline(examples[:6], dataset, top_k=3)
    metrics = aggregate_retriever_metrics(benchmark)

    assert "top_1_accuracy" in metrics
    assert "top_3_accuracy" in metrics
    assert metrics["example_count"] == 6
