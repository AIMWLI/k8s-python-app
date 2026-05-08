"""FastAPI 应用入口 — 模块级单例、ContextVar 全链路追踪、结构化日志。"""
from __future__ import annotations

import contextvars
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict

from app.config import settings

# ── ContextVar 全链路追踪 ──
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)

# 应用启动时间戳（进程级不可变）
_START_TIME: float = time.monotonic()

# ── 模块级单例 HTTP Client（Zero Lock, Zero GC）──
_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """获取全局 HTTP 连接池实例，仅在 lifespan 初始化后可用。"""
    if _http_client is None:
        raise RuntimeError("http_client not initialized — app not started")
    return _http_client


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _http_client
    _http_client = httpx.AsyncClient(
        http2=True,
        timeout=httpx.Timeout(10.0),
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=1000),
    )
    yield
    await _http_client.aclose()
    _http_client = None


app = FastAPI(
    title="k8s-python-app",
    lifespan=_lifespan,
    default_response_class=ORJSONResponse,
)


# ── Middleware: Request ID 注入 ──
@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Any:
    req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    token = request_id_ctx.set(req_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
    finally:
        request_id_ctx.reset(token)


# ── Routes ──
@app.get("/")
async def liveness_probe() -> dict[str, Any]:
    """Liveness 探针: 仅返回存活状态与核心标识。"""
    return {
        "status": "up",
        "service": "k8s-python-app",
        "env": "debug" if settings.DEBUG else "prod",
        "req_id": request_id_ctx.get(),
    }


@app.get("/health")
async def readiness_probe() -> dict[str, Any]:
    """Readiness 探针: 包含运行时间的详细状态。"""
    return {
        "status": "ok",
        "uptime_seconds": round(time.monotonic() - _START_TIME, 2),
        "host": settings.HOST,
        "port": settings.PORT,
        "req_id": request_id_ctx.get(),
    }


@app.get("/ping", response_class=PlainTextResponse)
async def ping() -> str:
    """极简心跳，规避 JSON 序列化开销。"""
    return "pong"


@app.get("/config")
async def get_config() -> dict[str, Any]:
    return {
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL,
    }


class EchoBody(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


@app.post("/echo")
async def echo(body: EchoBody) -> dict[str, Any]:
    return {"echo": body.model_dump()}
