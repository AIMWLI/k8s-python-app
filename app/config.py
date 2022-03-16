import os


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
