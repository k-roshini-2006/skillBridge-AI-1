import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Locate .env in backend dir or parent dir
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_paths = [
    BASE_DIR / ".env",
    Path(".env"),
    BASE_DIR.parent / ".env"
]
ENV_FILE = next((str(p) for p in env_paths if p.exists()), ".env")


class Settings(BaseSettings):
    APP_NAME: str = "SkillPath AI"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'skillpath.db'}"
    SECRET_KEY: str = "skillpath-ai-super-secret-key-2026-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    LLM_API_URL: str = ""
    LLM_API_KEY: str = ""
    MASTERY_THRESHOLD: float = 0.80
    WEAK_THRESHOLD: float = 0.50
    STRONG_THRESHOLD: float = 0.80

    class Config:
        env_file = ENV_FILE
        extra = "ignore"


settings = Settings()
