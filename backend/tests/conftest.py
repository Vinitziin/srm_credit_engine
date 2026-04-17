"""Integration fixtures.

Tests run against the same Postgres used by the app (configured via DATABASE_URL).
Each test starts with transactions and cedentes truncated — seed data (currencies,
receivable types, initial exchange rate) is preserved.

pytest-asyncio creates a fresh event loop per test by default, but asyncpg
connections cannot cross event loops. The `_reset_engine` autouse fixture
disposes the module-level engine before every test so the next awaited
operation opens a fresh connection bound to the current loop.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app import database
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def _reset_engine() -> AsyncGenerator[None, None]:
    await database.engine.dispose()
    async with database.async_session_factory() as session:
        await session.execute(text("TRUNCATE transactions, cedentes CASCADE"))
        await session.commit()
    yield
    await database.engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
