import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, List
import uuid
import contextvars
import time

import httpx
import orjson
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict

from app.config import settings

# --- Context Variables for Tracing ---
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

# App startup time for uptime tracking
START_TIME = time.time()

# --- Module-level Singleton (Zero Lock, Zero GC) ---
# HTTPX Client for all external requests
http_client = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(10.0),
    limits=httpx.Limits(max_keepalive_connections=100, max_connections=1000)
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Connections initialized
    yield
    # Shutdown: Close resources
    await http_client.aclose()


app = FastAPI(
    title="k8s-python-app",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Any:
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(req_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
    finally:
        request_id_ctx.reset(token)


@app.get("/")
async def liveness_probe() -> Dict[str, Any]:
    """工业级 Liveness 探针: 仅返回最基础的存活状态与核心标识"""
    return {
        "status": "up",
        "service": "k8s-python-app",
        "env": "debug" if settings.DEBUG else "prod",
        "req_id": request_id_ctx.get()
    }


@app.get("/health")
async def readiness_probe() -> Dict[str, Any]:
    """工业级 Readiness 探针: 包含运行时间、节点信息的详细状态"""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "host": settings.HOST,
        "port": settings.PORT,
        "req_id": request_id_ctx.get()
    }


@app.get("/ping", response_class=PlainTextResponse)
async def ping() -> str:
    """极简心跳接口，规避 JSON 序列化开销，直接返回 plain text"""
    return "pong"


@app.get("/config")
async def get_config() -> Dict[str, Any]:
    return {
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL,
    }


class EchoBody(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


@app.post("/echo")
async def echo(body: EchoBody) -> Dict[str, Any]:
    return {"echo": body.model_dump()}
