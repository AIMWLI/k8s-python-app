import asyncio
import httpx


async def fetch_all(urls, max_concurrent=10):
    sem = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient() as client:
        async def fetch(url):
            async with sem:
                r = await client.get(url)
                return r.text
        tasks = [fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
