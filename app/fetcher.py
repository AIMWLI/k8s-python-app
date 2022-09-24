import asyncio
import httpx


class AsyncFetcher:
    def __init__(self, base_url, timeout=10, max_retries=2):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self.max_retries = max_retries

    async def get(self, path):
        for _ in range(self.max_retries):
            try:
                r = await self.client.get(path)
                r.raise_for_status()
                return r.json()
            except (httpx.TimeoutException, httpx.HTTPStatusError):
                continue
        return None

    async def close(self):
        await self.client.aclose()
