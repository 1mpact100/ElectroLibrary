from fastapi import APIRouter, Depends, Request, Response, status

from app.repositories.book import BookRepository
from app.schemas.book import (
    BookCreate,
    BookListParams,
    BookListResponse,
    BookResponse,
    BookUpdate,
)
from app.services.book import BookService


router = APIRouter(prefix="/api/v1/books", tags=["books"])


def get_book_service(request: Request) -> BookService:
    repository = BookRepository(request.app.state.couchdb)
    return BookService(repository, request.app.state.redis)


@router.get("", response_model=BookListResponse)
async def list_books(
    params: BookListParams = Depends(),
    service: BookService = Depends(get_book_service),
):
    return await service.list(params)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, service: BookService = Depends(get_book_service)):
    return await service.get(book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    service: BookService = Depends(get_book_service),
):
    return await service.create(data)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    data: BookUpdate,
    service: BookService = Depends(get_book_service),
):
    return await service.update(book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    service: BookService = Depends(get_book_service),
):
    await service.delete(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
