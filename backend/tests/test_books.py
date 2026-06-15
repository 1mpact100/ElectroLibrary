async def create_references(client):
    author = (await client.post("/api/v1/authors", json={"name": "Автор"})).json()
    genre = (await client.post("/api/v1/genres", json={"name": "Роман"})).json()
    publisher = (await client.post("/api/v1/publishers", json={"name": "Азбука"})).json()
    return author, genre, publisher


async def create_book(client, title, year, author, genre, publisher):
    return await client.post(
        "/api/v1/books",
        json={
            "title": title,
            "publication_year": year,
            "author_id": author["id"],
            "genre_id": genre["id"],
            "publisher_id": publisher["id"],
        },
    )


async def test_book_crud_and_references(client):
    author, genre, publisher = await create_references(client)
    created = await create_book(
        client,
        "Мастер и Маргарита",
        1967,
        author,
        genre,
        publisher,
    )

    assert created.status_code == 201
    book = created.json()
    assert book["author"] == author
    assert book["genre"] == genre
    assert book["publisher"] == publisher

    in_use = await client.delete(f"/api/v1/authors/{author['id']}")
    assert in_use.status_code == 409
    assert in_use.json()["detail"]["code"] == "ENTITY_IN_USE"

    deleted = await client.delete(f"/api/v1/books/{book['id']}")
    assert deleted.status_code == 204

    author_deleted = await client.delete(f"/api/v1/authors/{author['id']}")
    assert author_deleted.status_code == 204


async def test_book_requires_correct_reference_type(client):
    author, genre, publisher = await create_references(client)

    response = await client.post(
        "/api/v1/books",
        json={
            "title": "Книга",
            "publication_year": 2000,
            "author_id": genre["id"],
            "genre_id": genre["id"],
            "publisher_id": publisher["id"],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Автор не найден"


async def test_book_list_filters_sorts_and_paginates(client):
    author, genre, publisher = await create_references(client)
    await create_book(client, "Альфа", 2001, author, genre, publisher)
    await create_book(client, "Гамма Альфа", 2010, author, genre, publisher)
    await create_book(client, "Бета", 1999, author, genre, publisher)

    first_page = await client.get("/api/v1/books", params={"limit": 2})
    first_data = first_page.json()
    assert [item["title"] for item in first_data["items"]] == ["Альфа", "Бета"]
    assert first_data["has_more"] is True

    second_page = await client.get(
        "/api/v1/books",
        params={"limit": 2, "bookmark": first_data["bookmark"]},
    )
    assert [item["title"] for item in second_page.json()["items"]] == ["Гамма Альфа"]

    search = await client.get("/api/v1/books", params={"search": "альфа"})
    assert [item["title"] for item in search.json()["items"]] == ["Альфа", "Гамма Альфа"]

    sorted_books = await client.get(
        "/api/v1/books",
        params={"sort": "publication_year", "order": "desc"},
    )
    assert [item["publication_year"] for item in sorted_books.json()["items"]] == [
        2010,
        2001,
        1999,
    ]
