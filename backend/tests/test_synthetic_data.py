from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues


def test_generate_synthetic_dialogues_shapes_grounded_examples() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset, seed=7, max_examples_per_entity=2)

    assert examples

    sample = examples[0]
    assert "history" in sample
    assert "user_message" in sample
    assert "target_entity_ids" in sample
    assert "fact_pack" in sample
    assert "response" in sample

    families = {example["dialogue_family"] for example in examples}
    assert "direct_lookup" in families
    assert "follow_up_location" in families

    follow_up = next(example for example in examples if example["dialogue_family"] == "follow_up_location")
    entity_name = follow_up["fact_pack"]["display_name"]
    assert entity_name in follow_up["response"]
