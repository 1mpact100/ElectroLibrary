from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.cache.redis import RedisCache
from app.config import get_settings
from app.database.couchdb import CouchDB
from app.errors import AppError
from app.routers.authors import router as authors_router
from app.routers.books import router as books_router
from app.routers.genres import router as genres_router
from app.routers.publishers import router as publishers_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.couchdb = CouchDB(settings)
    app.state.redis = RedisCache(settings)

    await app.state.couchdb.initialize()

    try:
        yield
    finally:
        await app.state.couchdb.close()
        await app.state.redis.close()


app = FastAPI(title="ElectroLibrary API", version="1.0.0", lifespan=lifespan)
app.include_router(authors_router)
app.include_router(books_router)
app.include_router(genres_router)
app.include_router(publishers_router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "detail": {
                "code": error.code,
                "message": error.message,
            }
        },
    )


@app.get("/api/v1/health")
async def health(request: Request) -> dict[str, object]:
    try:
        couchdb_available = await request.app.state.couchdb.ping()
    except Exception:
        couchdb_available = False

    try:
        redis_available = await request.app.state.redis.ping()
    except Exception:
        redis_available = False

    return {
        "status": "ok" if couchdb_available else "unavailable",
        "services": {
            "couchdb": couchdb_available,
            "redis": redis_available,
        },
    }
