import pytest


async def _create_cedente(client, document="11111111000111") -> str:
    resp = await client.post("/api/v1/cedentes", json={"name": "Test SA", "document": document})
    assert resp.status_code == 201
    return resp.json()["id"]


def _tx_payload(cedente_id: str, **overrides) -> dict:
    payload = {
        "cedente_id": cedente_id,
        "receivable_type": "Duplicata Mercantil",
        "face_value": "10000",
        "base_rate": "0.01",
        "term_months": 12,
        "currency_code": "BRL",
        "payment_currency_code": "BRL",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_post_transaction_same_currency(client):
    cedente_id = await _create_cedente(client)
    resp = await client.post("/api/v1/transactions", json=_tx_payload(cedente_id))
    assert resp.status_code == 201
    body = resp.json()
    assert body["exchange_rate_used"] is None
    # PV = 10000 / (1 + 0.01 + 0.015)^12 = 7435.55885045
    assert body["present_value"] == "7435.55885045"
    assert body["spread_applied"] == "0.015"
    assert body["status"] == "SETTLED"
    assert body["version"] == 1


@pytest.mark.asyncio
async def test_post_transaction_cross_currency_uses_fx(client):
    # Seed already includes USD -> BRL at 5.25
    cedente_id = await _create_cedente(client)
    resp = await client.post(
        "/api/v1/transactions",
        json=_tx_payload(cedente_id, currency_code="USD", payment_currency_code="BRL"),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["exchange_rate_used"] == "5.25000000"


@pytest.mark.asyncio
async def test_post_transaction_with_unknown_cedente_returns_404(client):
    resp = await client.post(
        "/api/v1/transactions",
        json=_tx_payload("00000000-0000-0000-0000-000000000000"),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_post_transaction_with_unknown_receivable_type_returns_404(client):
    cedente_id = await _create_cedente(client)
    resp = await client.post(
        "/api/v1/transactions",
        json=_tx_payload(cedente_id, receivable_type="Inexistente"),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_transaction_returns_persisted_values(client):
    cedente_id = await _create_cedente(client)
    created = await client.post("/api/v1/transactions", json=_tx_payload(cedente_id))
    tx_id = created.json()["id"]

    resp = await client.get(f"/api/v1/transactions/{tx_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == tx_id


@pytest.mark.asyncio
async def test_patch_status_with_correct_version_increments(client):
    cedente_id = await _create_cedente(client)
    created = await client.post("/api/v1/transactions", json=_tx_payload(cedente_id))
    tx_id = created.json()["id"]

    resp = await client.patch(
        f"/api/v1/transactions/{tx_id}/status",
        json={"status": "REVERSED", "version": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "REVERSED"
    assert body["version"] == 2


@pytest.mark.asyncio
async def test_patch_status_with_stale_version_returns_409(client):
    cedente_id = await _create_cedente(client)
    created = await client.post("/api/v1/transactions", json=_tx_payload(cedente_id))
    tx_id = created.json()["id"]

    ok = await client.patch(
        f"/api/v1/transactions/{tx_id}/status",
        json={"status": "REVERSED", "version": 1},
    )
    assert ok.status_code == 200

    stale = await client.patch(
        f"/api/v1/transactions/{tx_id}/status",
        json={"status": "SETTLED", "version": 1},
    )
    assert stale.status_code == 409


@pytest.mark.asyncio
async def test_patch_status_on_unknown_transaction_returns_404(client):
    resp = await client.patch(
        "/api/v1/transactions/00000000-0000-0000-0000-000000000000/status",
        json={"status": "REVERSED", "version": 1},
    )
    assert resp.status_code == 404
