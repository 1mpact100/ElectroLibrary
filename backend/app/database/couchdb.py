import httpx

from app.config import Settings
from app.errors import DatabaseRequestError, DatabaseUnavailableError, RevisionConflictError


INDEXES = [
    ("documents-by-type", ["type"]),
    ("references-by-name", ["type", "name"]),
    ("references-by-name-key", ["type", "name_key"]),
    ("books-by-title-key", ["type", "title_key"]),
    ("books-by-year", ["type", "publication_year"]),
    ("books-by-author", ["type", "author_id"]),
    ("books-by-genre", ["type", "genre_id"]),
    ("books-by-publisher", ["type", "publisher_id"]),
]


class CouchDB:
    def __init__(self, settings: Settings) -> None:
        self.database = settings.couchdb_database
        self.client = httpx.AsyncClient(
            base_url=settings.couchdb_url,
            auth=(settings.couchdb_user, settings.couchdb_password),
            timeout=10,
        )

    async def initialize(self) -> None:
        await self.request("PUT", f"/{self.database}", accepted_statuses={201, 412})

        for name, fields in INDEXES:
            await self.post(
                f"/{self.database}/_index",
                json={
                    "index": {"fields": fields},
                    "name": name,
                    "type": "json",
                },
            )

    async def ping(self) -> bool:
        response = await self.get("/_up")
        return response.status_code == 200

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        accepted_statuses: set[int] | None = None,
        **kwargs,
    ) -> httpx.Response:
        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.RequestError as error:
            raise DatabaseUnavailableError("CouchDB недоступна") from error

        if accepted_statuses and response.status_code in accepted_statuses:
            return response
        if response.status_code == 409:
            raise RevisionConflictError("Документ был изменён другим запросом")
        if response.status_code == 404:
            return response
        if response.status_code in (401, 403) or response.status_code >= 500:
            raise DatabaseUnavailableError("CouchDB недоступна")
        if response.status_code >= 400:
            raise DatabaseRequestError("Некорректный запрос к CouchDB")

        return response

    async def close(self) -> None:
        await self.client.aclose()
