from fastapi import APIRouter, Depends, Request, Response, status

from app.repositories.reference import ReferenceRepository
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate
from app.services.reference import ReferenceService


router = APIRouter(prefix="/api/v1/publishers", tags=["publishers"])


def get_publisher_service(request: Request) -> ReferenceService:
    repository = ReferenceRepository(
        request.app.state.couchdb,
        "publisher",
        "publisher_id",
        "Издательство не найдено",
        "Издательство с таким именем уже существует",
        "Невозможно удалить издательство, связанное с книгами",
    )
    return ReferenceService(repository, request.app.state.redis)


@router.get("", response_model=list[ReferenceResponse])
async def list_publishers(service: ReferenceService = Depends(get_publisher_service)):
    return await service.list()


@router.get("/{publisher_id}", response_model=ReferenceResponse)
async def get_publisher(
    publisher_id: str,
    service: ReferenceService = Depends(get_publisher_service),
):
    return await service.get(publisher_id)


@router.post("", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_publisher(
    data: ReferenceCreate,
    service: ReferenceService = Depends(get_publisher_service),
):
    return await service.create(data)


@router.put("/{publisher_id}", response_model=ReferenceResponse)
async def update_publisher(
    publisher_id: str,
    data: ReferenceUpdate,
    service: ReferenceService = Depends(get_publisher_service),
):
    return await service.update(publisher_id, data)


@router.delete("/{publisher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publisher(
    publisher_id: str,
    service: ReferenceService = Depends(get_publisher_service),
):
    await service.delete(publisher_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
