from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_WORKERS: int = 4
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = ""
    CORS_ORIGINS: str = "*"


settings = Settings()
