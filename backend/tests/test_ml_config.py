from app.ml.config import MLSettings


def test_ml_settings_defaults() -> None:
    settings = MLSettings()

    assert settings.project_name == "umat_nlp_project"
    assert settings.drive_root.endswith("umat_nlp_project")
