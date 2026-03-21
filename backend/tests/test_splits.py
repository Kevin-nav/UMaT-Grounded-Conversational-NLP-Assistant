from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset
from app.ml.synthetic_data import generate_synthetic_dialogues
from app.ml.splits import build_training_splits


def test_build_training_splits_excludes_held_out_families_and_duplicates() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    examples = generate_synthetic_dialogues(dataset, seed=11, max_examples_per_entity=2)
    splits = build_training_splits(
        examples,
        validation_families={"follow_up_location"},
        test_families={"direct_lookup"},
    )

    assert splits["train"]
    assert splits["validation"]
    assert splits["test"]

    train_keys = {item["example_key"] for item in splits["train"]}
    validation_keys = {item["example_key"] for item in splits["validation"]}
    test_keys = {item["example_key"] for item in splits["test"]}
    assert train_keys.isdisjoint(validation_keys)
    assert train_keys.isdisjoint(test_keys)
    assert validation_keys.isdisjoint(test_keys)

    assert {item["dialogue_family"] for item in splits["validation"]} == {"follow_up_location"}
    assert {item["dialogue_family"] for item in splits["test"]} == {"direct_lookup"}
