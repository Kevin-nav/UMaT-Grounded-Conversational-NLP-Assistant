from app.data.extract_markdown import extract_dataset


def test_extract_dataset_shapes_core_records() -> None:
    dataset = extract_dataset()

    assert len(dataset["faculties"]) >= 7
    assert len(dataset["departments"]) >= 15
    assert len(dataset["staff"]) >= 20
    assert len(dataset["location_guides"]) >= len(dataset["departments"])

    evans_obu = next(item for item in dataset["staff"] if item["full_name"] == "Evans Obu")
    assert evans_obu["faculty_id"] == "srid"
    assert "Cloud Computing" in evans_obu["specializations"]

    geomatics = next(item for item in dataset["departments"] if item["name"] == "Department of Geomatic Engineering")
    assert geomatics["campus"] == "Tarkwa Campus"

