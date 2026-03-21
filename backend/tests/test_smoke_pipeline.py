from pathlib import Path

from app.ml.config import MLSettings
from scripts.run_ml_smoke_test import run_smoke_pipeline


def test_run_smoke_pipeline_builds_artifacts() -> None:
    settings = MLSettings()
    result = run_smoke_pipeline(max_examples=12)

    assert Path(result["canonical_dataset"]).exists()
    assert Path(result["retriever_artifact"]).exists()
    assert Path(result["generator_artifact"]).exists()
    assert Path(result["evaluation_summary"]).exists()
    assert result["project_name"] == settings.project_name
