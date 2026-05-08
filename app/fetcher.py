"""异步 HTTP 抓取器 — 复用全局连接池，带重试与结构化错误日志。"""
from __future__ import annotations

import asyncio
from typing import Any

from httpx import HTTPStatusError, TimeoutException

from app.logger import get_logger
from app.main import get_http_client

_log = get_logger(__name__)


class AsyncFetcher:
    """零状态抓取器，复用全局 httpx.AsyncClient 连接池。"""
    __slots__ = ("base_url", "max_retries")

    def __init__(self, base_url: str, max_retries: int = 2) -> None:
        self.base_url = base_url
        self.max_retries = max_retries

    async def get(self, path: str) -> Any | None:
        url = f"{self.base_url}{path}"
        client = get_http_client()
        for attempt in range(self.max_retries):
            try:
                r = await client.get(url)
                r.raise_for_status()
                return r.json()
            except (TimeoutException, HTTPStatusError) as exc:
                if attempt == self.max_retries - 1:
                    _log.error(
                        "fetch failed url=%s attempt=%d/%d error=%s",
                        url, attempt + 1, self.max_retries, exc,
                    )
        return None


async def fetch_all(urls: list[str], max_concurrent: int = 10) -> list[Any]:
    """并发批量抓取，Semaphore 控制最大并发数。"""
    sem = asyncio.Semaphore(max_concurrent)
    client = get_http_client()

    async def _fetch(url: str) -> Any:
        async with sem:
            r = await client.get(url)
            return r.text

    return await asyncio.gather(*(_fetch(u) for u in urls), return_exceptions=True)
