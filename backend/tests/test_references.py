async def test_reference_crud_and_duplicate(client):
    created = await client.post("/api/v1/authors", json={"name": "Михаил Булгаков"})

    assert created.status_code == 201
    author = created.json()

    duplicate = await client.post("/api/v1/authors", json={"name": "  михаил булгаков  "})
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "DUPLICATE_ENTITY"

    updated = await client.put(
        f"/api/v1/authors/{author['id']}",
        json={"name": "М. А. Булгаков"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "М. А. Булгаков"

    deleted = await client.delete(f"/api/v1/authors/{author['id']}")
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/authors/{author['id']}")
    assert missing.status_code == 404


async def test_reference_name_is_required(client):
    response = await client.post("/api/v1/genres", json={"name": "   "})

    assert response.status_code == 422
