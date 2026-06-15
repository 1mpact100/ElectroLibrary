from fastapi import APIRouter, Depends, Request, Response, status

from app.repositories.reference import ReferenceRepository
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate
from app.services.reference import ReferenceService


router = APIRouter(prefix="/api/v1/genres", tags=["genres"])


def get_genre_service(request: Request) -> ReferenceService:
    repository = ReferenceRepository(
        request.app.state.couchdb,
        "genre",
        "genre_id",
        "Жанр не найден",
        "Жанр с таким именем уже существует",
        "Невозможно удалить жанр, связанный с книгами",
    )
    return ReferenceService(repository, request.app.state.redis)


@router.get("", response_model=list[ReferenceResponse])
async def list_genres(service: ReferenceService = Depends(get_genre_service)):
    return await service.list()


@router.get("/{genre_id}", response_model=ReferenceResponse)
async def get_genre(genre_id: str, service: ReferenceService = Depends(get_genre_service)):
    return await service.get(genre_id)


@router.post("", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    data: ReferenceCreate,
    service: ReferenceService = Depends(get_genre_service),
):
    return await service.create(data)


@router.put("/{genre_id}", response_model=ReferenceResponse)
async def update_genre(
    genre_id: str,
    data: ReferenceUpdate,
    service: ReferenceService = Depends(get_genre_service),
):
    return await service.update(genre_id, data)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: str,
    service: ReferenceService = Depends(get_genre_service),
):
    await service.delete(genre_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
