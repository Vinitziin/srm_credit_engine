import asyncio
import random
from decimal import Decimal

import structlog

logger = structlog.get_logger()

MOCK_RATES: dict[tuple[str, str], Decimal] = {
    ("USD", "BRL"): Decimal("5.25000000"),
    ("BRL", "USD"): Decimal("0.19047619"),
}


class ExternalRateError(Exception):
    """Raised when the external exchange rate API call fails."""


async def fetch_external_rate(from_code: str, to_code: str, max_retries: int = 3) -> Decimal:
    """Fetches exchange rate from a mocked external API with simple retry."""
    for attempt in range(1, max_retries + 1):
        try:
            return await _call_external_api(from_code, to_code)
        except ExternalRateError:
            if attempt == max_retries:
                logger.error(
                    "exchange_rate_fetch_failed",
                    from_code=from_code,
                    to_code=to_code,
                    attempts=max_retries,
                )
                raise
            wait = 0.5 * (2 ** (attempt - 1))
            logger.warning(
                "exchange_rate_fetch_retry",
                from_code=from_code,
                to_code=to_code,
                attempt=attempt,
                next_wait_seconds=wait,
            )
            await asyncio.sleep(wait)

    raise ExternalRateError("Unreachable")


async def _call_external_api(from_code: str, to_code: str) -> Decimal:
    """Simulates an external API call. Randomly fails ~20% of the time."""
    await asyncio.sleep(0.1)

    if random.random() < 0.2:  # noqa: S311
        raise ExternalRateError(f"External API unavailable for {from_code}/{to_code}")

    rate = MOCK_RATES.get((from_code, to_code))
    if rate is None:
        raise ExternalRateError(f"No rate available for {from_code}/{to_code}")

    return rate
