from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised runtime config (env‑driven)."""

    database_url: str
    jwt_secret: str = "change‑me"

    class Config:
        env_file = ".env"


settings = Settings()