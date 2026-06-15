from app.cache.redis import RedisCache
from app.repositories.reference import ReferenceRepository
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate


class ReferenceService:
    def __init__(self, repository: ReferenceRepository, cache: RedisCache) -> None:
        self.repository = repository
        self.cache = cache

    async def list(self) -> list[ReferenceResponse]:
        documents = await self.repository.list()
        return [self.to_response(document) for document in documents]

    async def get(self, document_id: str) -> ReferenceResponse:
        document = await self.repository.get(document_id)
        return self.to_response(document)

    async def create(self, data: ReferenceCreate) -> ReferenceResponse:
        document = await self.repository.create(data.name)
        await self.cache.invalidate("books")
        return self.to_response(document)

    async def update(self, document_id: str, data: ReferenceUpdate) -> ReferenceResponse:
        document = await self.repository.update(document_id, data.name)
        await self.cache.invalidate("books")
        return self.to_response(document)

    async def delete(self, document_id: str) -> None:
        await self.repository.delete(document_id)
        await self.cache.invalidate("books")

    @staticmethod
    def to_response(document: dict) -> ReferenceResponse:
        return ReferenceResponse(id=document["_id"], name=document["name"])
