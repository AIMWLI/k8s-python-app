from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict

from app.config import settings
from app.cache import TTLCache

cache = TTLCache(ttl=30)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(title="k8s-python-app", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello from Python!"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "host": settings.HOST,
        "port": settings.PORT,
    }


@app.get("/config")
def get_config():
    return {
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL,
    }


class EchoBody(BaseModel):
    model_config = ConfigDict(extra="allow")


@app.post("/echo")
def echo(body: EchoBody) -> dict:
    return {"echo": body.model_dump()}
