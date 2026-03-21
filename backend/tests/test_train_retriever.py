from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues
from app.ml.train_retriever import RetrieverTrainingConfig, run_retriever_training


def test_run_retriever_training_returns_metrics_and_artifact_manifest() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset, seed=13, max_examples_per_entity=2)
    output_dir = Path("backend/artifacts/test_retriever")
    config = RetrieverTrainingConfig(output_dir=output_dir)
    result = run_retriever_training(dataset, examples[:10], config=config)

    assert "top_1_accuracy" in result.metrics
    assert "top_3_accuracy" in result.metrics
    assert result.artifact_path.exists()
