from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    couchdb_url: str = "http://localhost:5984"
    couchdb_database: str = "electrolibrary"
    couchdb_user: str = "admin"
    couchdb_password: str = "password"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    cache_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
