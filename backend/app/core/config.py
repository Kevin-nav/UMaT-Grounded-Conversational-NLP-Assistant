from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = ROOT_DIR / "data"
SEED_DIR = DATA_DIR / "seed"
RAW_MARKDOWN_PATH = ROOT_DIR / "UMaT Lecturer Information Gathering.md"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="UMAT_", env_file=".env", extra="ignore")

    app_name: str = "UMaT Staff Chatbot"
    api_prefix: str = "/api"
    secret_key: str = "change-me-for-production"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'app.db').as_posix()}"
    frontend_origin: str = "http://localhost:5173"
    bootstrap_admin_email: str = "admin@umat.edu.gh"
    bootstrap_admin_password: str = "Admin123!"
    bootstrap_admin_name: str = "UMaT Super Admin"
    bootstrap_editor_email: str = "editor@umat.edu.gh"
    bootstrap_editor_password: str = "Editor123!"
    bootstrap_viewer_email: str = "viewer@umat.edu.gh"
    bootstrap_viewer_password: str = "Viewer123!"
    ml_experimental_enabled: bool = False
    ml_retriever_artifact_path: str = str(BACKEND_DIR / "artifacts" / "umat_nlp_project" / "retriever" / "retriever_artifact.json")
    ml_generator_artifact_path: str = str(BACKEND_DIR / "artifacts" / "umat_nlp_project" / "generator" / "generator_artifact.json")


@lru_cache
def get_settings() -> Settings:
    return Settings()
