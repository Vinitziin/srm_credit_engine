from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.pricing_service import price_receivable


@pytest.mark.asyncio
async def test_same_currency_skips_fx_lookup():
    session = MagicMock()
    result = await price_receivable(
        session,
        face_value=Decimal("10000"),
        base_rate=Decimal("0.01"),
        term_months=12,
        receivable_type="Duplicata Mercantil",
        currency_code="BRL",
        payment_currency_code="BRL",
    )
    assert result.exchange_rate_used is None
    assert result.present_value == result.present_value_in_payment_currency
    assert result.spread_applied == Decimal("0.015")


@pytest.mark.asyncio
async def test_cross_currency_applies_rate(monkeypatch):
    fake_rate = MagicMock()
    fake_rate.rate = Decimal("0.20")
    mock_get_latest = AsyncMock(return_value=(fake_rate, "BRL", "USD"))
    monkeypatch.setattr(
        "app.services.pricing_service.exchange_rate_repository.get_latest",
        mock_get_latest,
    )

    result = await price_receivable(
        MagicMock(),
        face_value=Decimal("1000"),
        base_rate=Decimal("0"),
        term_months=0,
        receivable_type="Duplicata Mercantil",
        currency_code="BRL",
        payment_currency_code="USD",
    )
    assert result.exchange_rate_used == Decimal("0.20")
    assert result.present_value == Decimal("1000.00000000")
    assert result.present_value_in_payment_currency == Decimal("200.00000000")


@pytest.mark.asyncio
async def test_missing_fx_rate_raises_404(monkeypatch):
    mock_get_latest = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.services.pricing_service.exchange_rate_repository.get_latest",
        mock_get_latest,
    )
    with pytest.raises(HTTPException) as exc:
        await price_receivable(
            MagicMock(),
            face_value=Decimal("100"),
            base_rate=Decimal("0"),
            term_months=0,
            receivable_type="Duplicata Mercantil",
            currency_code="BRL",
            payment_currency_code="USD",
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_unknown_receivable_type_raises_400():
    with pytest.raises(HTTPException) as exc:
        await price_receivable(
            MagicMock(),
            face_value=Decimal("100"),
            base_rate=Decimal("0"),
            term_months=1,
            receivable_type="Foo",
            currency_code="BRL",
            payment_currency_code="BRL",
        )
    assert exc.value.status_code == 400
