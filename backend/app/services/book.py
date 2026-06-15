import asyncio

from app.cache.redis import RedisCache
from app.repositories.book import BookRepository
from app.schemas.book import (
    BookCreate,
    BookListParams,
    BookListResponse,
    BookResponse,
    BookUpdate,
)
from app.schemas.reference import ReferenceResponse


class BookService:
    def __init__(self, repository: BookRepository, cache: RedisCache) -> None:
        self.repository = repository
        self.cache = cache

    async def list(self, params: BookListParams) -> BookListResponse:
        cache_params = params.model_dump(mode="json", exclude_none=True)
        cached = await self.cache.get("books", cache_params)
        if cached:
            return BookListResponse.model_validate_json(cached)

        books, bookmark, has_more = await self.repository.list(params)
        items = await asyncio.gather(*(self.to_response(book) for book in books))
        result = BookListResponse(items=items, bookmark=bookmark, has_more=has_more)
        await self.cache.set("books", cache_params, result.model_dump_json())
        return result

    async def get(self, book_id: str) -> BookResponse:
        book = await self.repository.get(book_id)
        return await self.to_response(book)

    async def create(self, data: BookCreate) -> BookResponse:
        await self.get_references(data.author_id, data.genre_id, data.publisher_id)
        book = await self.repository.create(data.model_dump())
        await self.cache.invalidate("books")
        return await self.to_response(book)

    async def update(self, book_id: str, data: BookUpdate) -> BookResponse:
        await self.repository.get(book_id)
        await self.get_references(data.author_id, data.genre_id, data.publisher_id)
        book = await self.repository.update(book_id, data.model_dump())
        await self.cache.invalidate("books")
        return await self.to_response(book)

    async def delete(self, book_id: str) -> None:
        await self.repository.delete(book_id)
        await self.cache.invalidate("books")

    async def to_response(self, book: dict) -> BookResponse:
        author, genre, publisher = await self.get_references(
            book["author_id"],
            book["genre_id"],
            book["publisher_id"],
        )
        return BookResponse(
            id=book["_id"],
            title=book["title"],
            publication_year=book["publication_year"],
            author=self.reference_response(author),
            genre=self.reference_response(genre),
            publisher=self.reference_response(publisher),
        )

    async def get_references(
        self,
        author_id: str,
        genre_id: str,
        publisher_id: str,
    ) -> tuple[dict, dict, dict]:
        return await asyncio.gather(
            self.repository.get_document(author_id, "author", "Автор не найден"),
            self.repository.get_document(genre_id, "genre", "Жанр не найден"),
            self.repository.get_document(
                publisher_id,
                "publisher",
                "Издательство не найдено",
            ),
        )

    @staticmethod
    def reference_response(document: dict) -> ReferenceResponse:
        return ReferenceResponse(id=document["_id"], name=document["name"])
