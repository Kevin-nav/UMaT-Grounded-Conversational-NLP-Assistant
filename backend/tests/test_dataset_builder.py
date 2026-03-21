from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.ml.dataset_builder import export_canonical_dataset


def test_export_canonical_dataset_shapes_staff_records() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_if_empty(db)
        dataset = export_canonical_dataset(db)

    assert dataset["staff"]

    staff_record = dataset["staff"][0]
    assert "entity_id" in staff_record
    assert "entity_type" in staff_record
    assert "display_name" in staff_record
    assert "aliases" in staff_record
    assert "facts" in staff_record

    evans_obu = next(item for item in dataset["staff"] if item["display_name"] == "Evans Obu")
    assert evans_obu["entity_id"] == "evans-obu"
    assert evans_obu["entity_type"] == "staff"
    assert "Cloud Computing" in evans_obu["facts"]["specializations"]
