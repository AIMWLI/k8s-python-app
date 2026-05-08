"""结构化 JSON 日志 — 模块级单例，全链路 Request ID 追踪。"""
from __future__ import annotations

import logging
import sys
from typing import Any

import orjson

from app.config import settings


class _JSONFormatter(logging.Formatter):
    """零依赖结构化 JSON 日志格式器，底层用 orjson 消除序列化瓶颈。"""
    __slots__ = ()

    def format(self, record: logging.LogRecord) -> str:
        # 延迟导入避免循环引用（main -> logger -> main）
        from app.main import request_id_ctx
        payload: dict[str, Any] = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "req_id": request_id_ctx.get(""),
        }
        if record.exc_info and record.exc_info[0] is not None:
            payload["traceback"] = self.formatException(record.exc_info)
        return orjson.dumps(payload).decode()


def get_logger(name: str) -> logging.Logger:
    """获取或创建命名 Logger，幂等安全。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JSONFormatter())
        logger.addHandler(handler)
    return logger
