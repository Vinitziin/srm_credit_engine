import pytest


async def _create_cedente(client, name, document) -> str:
    resp = await client.post(
        "/api/v1/cedentes", json={"name": name, "document": document}
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_tx(
    client,
    cedente_id: str,
    *,
    currency: str = "BRL",
    payment_currency: str = "BRL",
) -> dict:
    resp = await client.post(
        "/api/v1/transactions",
        json={
            "cedente_id": cedente_id,
            "receivable_type": "Duplicata Mercantil",
            "face_value": "1000",
            "base_rate": "0.01",
            "term_months": 6,
            "currency_code": currency,
            "payment_currency_code": payment_currency,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_statements_empty_returns_zero(client):
    resp = await client.get("/api/v1/reports/statements")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"page": 1, "page_size": 50, "total": 0, "items": []}


@pytest.mark.asyncio
async def test_statements_returns_items_ordered_desc(client):
    cid = await _create_cedente(client, "Acme", "11111111000111")
    tx_a = await _create_tx(client, cid)
    tx_b = await _create_tx(client, cid)
    tx_c = await _create_tx(client, cid)

    resp = await client.get("/api/v1/reports/statements")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    ids = [item["id"] for item in body["items"]]
    assert ids == [tx_c["id"], tx_b["id"], tx_a["id"]]


@pytest.mark.asyncio
async def test_statements_pagination(client):
    cid = await _create_cedente(client, "Acme", "22222222000122")
    for _ in range(5):
        await _create_tx(client, cid)

    page1 = await client.get(
        "/api/v1/reports/statements", params={"page": 1, "page_size": 2}
    )
    page2 = await client.get(
        "/api/v1/reports/statements", params={"page": 2, "page_size": 2}
    )
    page3 = await client.get(
        "/api/v1/reports/statements", params={"page": 3, "page_size": 2}
    )

    assert page1.json()["total"] == 5
    assert len(page1.json()["items"]) == 2
    assert len(page2.json()["items"]) == 2
    assert len(page3.json()["items"]) == 1

    all_ids = (
        [i["id"] for i in page1.json()["items"]]
        + [i["id"] for i in page2.json()["items"]]
        + [i["id"] for i in page3.json()["items"]]
    )
    assert len(set(all_ids)) == 5


@pytest.mark.asyncio
async def test_statements_filter_by_cedente(client):
    cid_a = await _create_cedente(client, "A", "33333333000133")
    cid_b = await _create_cedente(client, "B", "44444444000144")
    await _create_tx(client, cid_a)
    await _create_tx(client, cid_a)
    await _create_tx(client, cid_b)

    resp = await client.get(
        "/api/v1/reports/statements", params={"cedente_id": cid_a}
    )
    body = resp.json()
    assert body["total"] == 2
    assert all(item["cedente_name"] == "A" for item in body["items"])


@pytest.mark.asyncio
async def test_statements_filter_by_payment_currency(client):
    cid = await _create_cedente(client, "Acme", "55555555000155")
    # same currency = BRL->BRL
    await _create_tx(client, cid)
    # cross-currency USD->BRL (seeded rate exists)
    await _create_tx(client, cid, currency="USD", payment_currency="BRL")

    resp_brl = await client.get(
        "/api/v1/reports/statements", params={"currency_code": "BRL"}
    )
    assert resp_brl.json()["total"] == 2

    resp_usd = await client.get(
        "/api/v1/reports/statements", params={"currency_code": "USD"}
    )
    assert resp_usd.json()["total"] == 0


@pytest.mark.asyncio
async def test_statements_filter_by_status(client):
    cid = await _create_cedente(client, "Acme", "66666666000166")
    tx1 = await _create_tx(client, cid)
    await _create_tx(client, cid)

    # move one to REVERSED
    patch = await client.patch(
        f"/api/v1/transactions/{tx1['id']}/status",
        json={"status": "REVERSED", "version": 1},
    )
    assert patch.status_code == 200

    settled = await client.get(
        "/api/v1/reports/statements", params={"status": "SETTLED"}
    )
    reversed_ = await client.get(
        "/api/v1/reports/statements", params={"status": "REVERSED"}
    )
    assert settled.json()["total"] == 1
    assert reversed_.json()["total"] == 1


@pytest.mark.asyncio
async def test_statements_filter_by_date_range(client):
    from datetime import date, timedelta

    cid = await _create_cedente(client, "Acme", "77777777000177")
    await _create_tx(client, cid)

    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # date_to=today should include today (inclusive end)
    resp_in = await client.get(
        "/api/v1/reports/statements",
        params={"date_from": today.isoformat(), "date_to": today.isoformat()},
    )
    assert resp_in.json()["total"] == 1

    # window entirely before today -> empty
    resp_out = await client.get(
        "/api/v1/reports/statements",
        params={
            "date_from": yesterday.isoformat(),
            "date_to": yesterday.isoformat(),
        },
    )
    assert resp_out.json()["total"] == 0

    # from tomorrow -> empty
    resp_future = await client.get(
        "/api/v1/reports/statements",
        params={"date_from": tomorrow.isoformat()},
    )
    assert resp_future.json()["total"] == 0


@pytest.mark.asyncio
async def test_statements_invalid_currency_code_returns_422(client):
    resp = await client.get(
        "/api/v1/reports/statements", params={"currency_code": "EURO"}
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_statements_page_size_upper_bound(client):
    resp = await client.get(
        "/api/v1/reports/statements", params={"page_size": 500}
    )
    assert resp.status_code == 422
