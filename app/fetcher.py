import asyncio
import httpx


class AsyncFetcher:
    def __init__(self, base_url, timeout=10):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def get(self, path):
        r = await self.client.get(path)
        r.raise_for_status()
        return r.json()

    async def close(self):
        await self.client.aclose()
