import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client


@pytest.fixture(autouse=True)
async def clean_storage(client):
    couchdb = app.state.couchdb
    await couchdb.client.delete(f"/{couchdb.database}")
    await couchdb.initialize()
    await app.state.redis.client.flushdb()
