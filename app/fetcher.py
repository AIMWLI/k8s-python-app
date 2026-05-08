from typing import Optional, Any, List
import asyncio
from httpx import HTTPStatusError, TimeoutException

from app.main import http_client


class AsyncFetcher:
    """
    Zero-state, module-level usage fetcher wrapper.
    Re-uses the global http_client with http2=True and brotli.
    """
    __slots__ = ("base_url", "max_retries")

    def __init__(self, base_url: str, max_retries: int = 2):
        self.base_url = base_url
        self.max_retries = max_retries

    async def get(self, path: str) -> Optional[Any]:
        url = f"{self.base_url}{path}"
        # Retry loop without time.sleep, using pure async flow
        for attempt in range(self.max_retries):
            try:
                r = await http_client.get(url)
                r.raise_for_status()
                # Use httpx built-in orjson integration (or .json() which is optimized internally)
                # For pure orjson, we could do: orjson.loads(r.read())
                return r.json()
            except (TimeoutException, HTTPStatusError) as e:
                # Need to log instead of swallowing silently, per constraints.
                # Here we just print, but production code should use structlog
                if attempt == self.max_retries - 1:
                    print(f"fetch error {url}: {e.__class__.__name__}")
                continue
        return None

    # No manual close() needed, lifespan handles global http_client.aclose()


async def fetch_all(urls: List[str], max_concurrent: int = 10) -> List[Any]:
    sem = asyncio.Semaphore(max_concurrent)

    async def _fetch(url: str) -> Any:
        async with sem:
            r = await http_client.get(url)
            return r.text

    # Uses generator expression rather than list comprehension inside gather
    return await asyncio.gather(*(_fetch(u) for u in urls), return_exceptions=True)
