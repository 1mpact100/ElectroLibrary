from uuid import uuid4

from app.database.couchdb import CouchDB
from app.errors import DuplicateEntityError, EntityInUseError, EntityNotFoundError


class ReferenceRepository:
    def __init__(
        self,
        couchdb: CouchDB,
        document_type: str,
        book_field: str,
        not_found_message: str,
        duplicate_message: str,
        in_use_message: str,
    ) -> None:
        self.couchdb = couchdb
        self.document_type = document_type
        self.book_field = book_field
        self.not_found_message = not_found_message
        self.duplicate_message = duplicate_message
        self.in_use_message = in_use_message

    async def list(self) -> list[dict]:
        response = await self.couchdb.post(
            f"/{self.couchdb.database}/_find",
            json={
                "selector": {"type": self.document_type},
                "limit": 1000,
            },
        )
        return sorted(response.json()["docs"], key=lambda item: item["name"].casefold())

    async def get(self, document_id: str) -> dict:
        response = await self.couchdb.get(f"/{self.couchdb.database}/{document_id}")
        if response.status_code == 404:
            raise EntityNotFoundError(self.not_found_message)
        document = response.json()
        if document.get("type") != self.document_type:
            raise EntityNotFoundError(self.not_found_message)
        return document

    async def create(self, name: str) -> dict:
        await self.ensure_unique(name)
        document = {
            "_id": f"{self.document_type}:{uuid4()}",
            "type": self.document_type,
            "name": name,
            "name_key": name.casefold(),
        }
        await self.couchdb.put(
            f"/{self.couchdb.database}/{document['_id']}",
            json=document,
        )
        return document

    async def update(self, document_id: str, name: str) -> dict:
        document = await self.get(document_id)
        await self.ensure_unique(name, exclude_id=document_id)
        document["name"] = name
        document["name_key"] = name.casefold()

        await self.couchdb.put(
            f"/{self.couchdb.database}/{document_id}",
            json=document,
        )
        return document

    async def delete(self, document_id: str) -> None:
        document = await self.get(document_id)
        if await self.is_used(document_id):
            raise EntityInUseError(self.in_use_message)

        await self.couchdb.delete(
            f"/{self.couchdb.database}/{document_id}",
            params={"rev": document["_rev"]},
        )

    async def ensure_unique(self, name: str, exclude_id: str | None = None) -> None:
        response = await self.couchdb.post(
            f"/{self.couchdb.database}/_find",
            json={
                "selector": {
                    "type": self.document_type,
                    "name_key": name.casefold(),
                },
                "limit": 1,
            },
        )
        documents = response.json()["docs"]
        if documents and documents[0]["_id"] != exclude_id:
            raise DuplicateEntityError(self.duplicate_message)

    async def is_used(self, document_id: str) -> bool:
        response = await self.couchdb.post(
            f"/{self.couchdb.database}/_find",
            json={
                "selector": {
                    "type": "book",
                    self.book_field: document_id,
                },
                "limit": 1,
            },
        )
        return bool(response.json()["docs"])
