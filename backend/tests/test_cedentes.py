import pytest


@pytest.mark.asyncio
async def test_create_and_list_cedente(client):
    resp = await client.post(
        "/api/v1/cedentes",
        json={"name": "Acme SA", "document": "11222333000155"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Acme SA"
    assert body["document"] == "11222333000155"
    assert "id" in body

    list_resp = await client.get("/api/v1/cedentes")
    assert list_resp.status_code == 200
    assert any(c["id"] == body["id"] for c in list_resp.json())


@pytest.mark.asyncio
async def test_duplicate_document_returns_409(client):
    payload = {"name": "Acme", "document": "99888777000100"}
    first = await client.post("/api/v1/cedentes", json=payload)
    assert first.status_code == 201

    dup = await client.post(
        "/api/v1/cedentes", json={"name": "Other", "document": "99888777000100"}
    )
    assert dup.status_code == 409
