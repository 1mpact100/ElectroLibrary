import httpx
import pytest

from app.config import Settings
from app.database.couchdb import CouchDB
from app.errors import DatabaseUnavailableError, RevisionConflictError
from app.main import app


async def test_couchdb_conflict_is_converted():
    couchdb = CouchDB(Settings())
    await couchdb.client.aclose()
    couchdb.client = httpx.AsyncClient(
        base_url="http://couchdb",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(409, request=request)
        )
    )

    with pytest.raises(RevisionConflictError):
        await couchdb.put("/document")

    await couchdb.close()


async def test_api_returns_503_when_couchdb_is_unavailable(client, monkeypatch):
    async def unavailable(*args, **kwargs):
        raise DatabaseUnavailableError("CouchDB недоступна")

    monkeypatch.setattr(app.state.couchdb, "post", unavailable)

    response = await client.get("/api/v1/books")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "DATABASE_UNAVAILABLE",
            "message": "CouchDB недоступна",
        }
    }
