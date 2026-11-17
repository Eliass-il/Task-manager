import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_endpoint_returns_success(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Works": "Fine"}