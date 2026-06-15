import re
from uuid import uuid4

from app.database.couchdb import CouchDB
from app.errors import EntityNotFoundError
from app.schemas.book import BookListParams


class BookRepository:
    def __init__(self, couchdb: CouchDB) -> None:
        self.couchdb = couchdb

    async def list(self, params: BookListParams) -> tuple[list[dict], str | None, bool]:
        sort_field = "title_key" if params.sort == "title" else "publication_year"
        selector = {
            "type": "book",
            sort_field: {"$gte": "" if sort_field == "title_key" else 1000},
        }

        if params.author_id:
            selector["author_id"] = params.author_id
        if params.genre_id:
            selector["genre_id"] = params.genre_id
        if params.publisher_id:
            selector["publisher_id"] = params.publisher_id
        if params.year:
            selector["publication_year"] = params.year
        if params.search:
            selector["title_key"] = {"$regex": re.escape(params.search.casefold())}

        query = {
            "selector": selector,
            "sort": [{sort_field: params.order}],
            "limit": params.limit,
        }
        if params.bookmark:
            query["bookmark"] = params.bookmark

        response = await self.couchdb.post(
            f"/{self.couchdb.database}/_find",
            json=query,
        )
        result = response.json()
        if not result["docs"]:
            return [], None, False

        bookmark = result["bookmark"]
        has_more = await self.has_more(selector, sort_field, params.order, bookmark)
        return result["docs"], bookmark if has_more else None, has_more

    async def has_more(
        self,
        selector: dict,
        sort_field: str,
        order: str,
        bookmark: str,
    ) -> bool:
        response = await self.couchdb.post(
            f"/{self.couchdb.database}/_find",
            json={
                "selector": selector,
                "sort": [{sort_field: order}],
                "limit": 1,
                "bookmark": bookmark,
            },
        )
        return bool(response.json()["docs"])

    async def get(self, book_id: str) -> dict:
        response = await self.couchdb.get(f"/{self.couchdb.database}/{book_id}")
        if response.status_code == 404:
            raise EntityNotFoundError("Книга не найдена")
        book = response.json()
        if book.get("type") != "book":
            raise EntityNotFoundError("Книга не найдена")
        return book

    async def get_document(self, document_id: str, document_type: str, message: str) -> dict:
        response = await self.couchdb.get(f"/{self.couchdb.database}/{document_id}")
        if response.status_code == 404:
            raise EntityNotFoundError(message)
        document = response.json()
        if document.get("type") != document_type:
            raise EntityNotFoundError(message)
        return document

    async def create(self, data: dict) -> dict:
        book = {
            "_id": f"book:{uuid4()}",
            "type": "book",
            **data,
        }
        book["title_key"] = book["title"].casefold()
        await self.couchdb.put(
            f"/{self.couchdb.database}/{book['_id']}",
            json=book,
        )
        return book

    async def update(self, book_id: str, data: dict) -> dict:
        book = await self.get(book_id)
        book.update(data)
        book["title_key"] = book["title"].casefold()
        await self.couchdb.put(
            f"/{self.couchdb.database}/{book_id}",
            json=book,
        )
        return book

    async def delete(self, book_id: str) -> None:
        book = await self.get(book_id)
        await self.couchdb.delete(
            f"/{self.couchdb.database}/{book_id}",
            params={"rev": book["_rev"]},
        )
