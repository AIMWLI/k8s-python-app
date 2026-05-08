from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_WORKERS: int = 4
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = ""
    CORS_ORIGINS: str = "*"


# Module-level singleton
settings = Settings()
