from fastapi import APIRouter, Depends, Request, Response, status

from app.repositories.reference import ReferenceRepository
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate
from app.services.reference import ReferenceService


router = APIRouter(prefix="/api/v1/authors", tags=["authors"])


def get_author_service(request: Request) -> ReferenceService:
    repository = ReferenceRepository(
        request.app.state.couchdb,
        "author",
        "author_id",
        "Автор не найден",
        "Автор с таким именем уже существует",
        "Невозможно удалить автора, связанного с книгами",
    )
    return ReferenceService(repository, request.app.state.redis)


@router.get("", response_model=list[ReferenceResponse])
async def list_authors(service: ReferenceService = Depends(get_author_service)):
    return await service.list()


@router.get("/{author_id}", response_model=ReferenceResponse)
async def get_author(author_id: str, service: ReferenceService = Depends(get_author_service)):
    return await service.get(author_id)


@router.post("", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: ReferenceCreate,
    service: ReferenceService = Depends(get_author_service),
):
    return await service.create(data)


@router.put("/{author_id}", response_model=ReferenceResponse)
async def update_author(
    author_id: str,
    data: ReferenceUpdate,
    service: ReferenceService = Depends(get_author_service),
):
    return await service.update(author_id, data)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: str,
    service: ReferenceService = Depends(get_author_service),
):
    await service.delete(author_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
