from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.reference import ReferenceResponse


BookTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=300),
]
BookSearch = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=300),
]


class BookCreate(BaseModel):
    title: BookTitle
    publication_year: int = Field(ge=1000, le=date.today().year)
    author_id: str
    genre_id: str
    publisher_id: str


class BookUpdate(BookCreate):
    pass


class BookResponse(BaseModel):
    id: str
    title: str
    publication_year: int
    author: ReferenceResponse
    genre: ReferenceResponse
    publisher: ReferenceResponse


class BookListParams(BaseModel):
    author_id: str | None = None
    genre_id: str | None = None
    publisher_id: str | None = None
    year: int | None = Field(default=None, ge=1000, le=date.today().year)
    search: BookSearch | None = None
    sort: Literal["title", "publication_year"] = "title"
    order: Literal["asc", "desc"] = "asc"
    limit: int = Field(default=10, ge=1, le=100)
    bookmark: str | None = None


class BookListResponse(BaseModel):
    items: list[BookResponse]
    bookmark: str | None
    has_more: bool
