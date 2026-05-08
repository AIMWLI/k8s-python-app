"""全局配置 — pydantic-settings 环境变量注入，模块级单例。"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_WORKERS: int = 4
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = ""
    CORS_ORIGINS: str = "*"


# 模块级单例 — Import System 保证零锁、O(1) 线程安全
settings: _Settings = _Settings()
