from __future__ import annotations

from app.core.config import RAW_MARKDOWN_PATH
from app.data.extract_markdown import extract_dataset


def test_extract_dataset_builds_expected_collections() -> None:
    payload = extract_dataset(RAW_MARKDOWN_PATH)

    assert len(payload["faculties"]) >= 7
    assert len(payload["departments"]) >= 15
    assert len(payload["staff"]) >= 20
    assert any(member["full_name"] == "Richard K. Amankwah" for member in payload["staff"])
    assert any(member["full_name"] == "Evans Obu" for member in payload["staff"])


def test_extracted_staff_preserves_department_location_context() -> None:
    payload = extract_dataset(RAW_MARKDOWN_PATH)
    staff_by_name = {member["full_name"]: member for member in payload["staff"]}

    assert staff_by_name["Evans Obu"]["campus"] == "Essikado Campus"
    assert staff_by_name["Evans Obu"]["department_id"] == "department-of-computing-and-data-analytics-engineering"
    assert staff_by_name["Anthony Ewusi"]["faculty_id"] == "fges"
