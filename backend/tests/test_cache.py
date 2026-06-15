from app.main import app


async def test_book_list_cache_is_invalidated(client):
    await client.get("/api/v1/books")

    version_before = await app.state.redis.client.get("books:cache_version")
    keys_before = await app.state.redis.client.keys("books:list:*")
    assert version_before == "1"
    assert len(keys_before) == 1

    await client.post("/api/v1/authors", json={"name": "Автор"})

    version_after = await app.state.redis.client.get("books:cache_version")
    assert version_after == "2"
