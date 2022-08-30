import pytest
from app.concurrency import fetch_all


@pytest.mark.asyncio
async def test_fetch_all():
    urls = ["https://httpbin.org/get", "https://httpbin.org/ip"]
    results = await fetch_all(urls)
    assert len(results) == 2
    for r in results:
        assert isinstance(r, str)
