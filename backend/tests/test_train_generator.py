from pathlib import Path

from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues
from app.ml.train_generator import GeneratorTrainingConfig, prepare_generator_examples, run_generator_training


def test_run_generator_training_transforms_examples_and_returns_metrics() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset, seed=17, max_examples_per_entity=2)
    prepared = prepare_generator_examples(examples[:8])
    assert prepared
    assert {"input_text", "target_text"} <= set(prepared[0])

    output_dir = Path("backend/artifacts/test_generator")
    config = GeneratorTrainingConfig(output_dir=output_dir)
    result = run_generator_training(examples[:8], config=config)
    assert "train_loss" in result.metrics
    assert "validation_score" in result.metrics
    assert result.artifact_path.exists()
