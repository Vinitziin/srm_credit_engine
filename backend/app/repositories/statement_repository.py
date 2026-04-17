"""Statement report repository.

Uses SQLAlchemy Core `text()` with bound parameters for performance over the
ORM on analytical queries — exactly what the case asks for. The same WHERE
clause is shared between the COUNT and the paginated SELECT.

Never interpolate filter values into the SQL string: every dynamic piece is a
named bindparam to keep this injection-free.
"""

from datetime import timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.statements import StatementFilters, StatementItem


def _build_where(filters: StatementFilters) -> tuple[str, dict]:
    conditions: list[str] = []
    params: dict = {}

    if filters.date_from is not None:
        conditions.append("t.created_at >= :date_from")
        params["date_from"] = filters.date_from
    if filters.date_to is not None:
        # inclusive end: include everything on date_to, exclude the next day.
        conditions.append("t.created_at < :date_to_excl")
        params["date_to_excl"] = filters.date_to + timedelta(days=1)
    if filters.cedente_id is not None:
        conditions.append("t.cedente_id = :cedente_id")
        params["cedente_id"] = filters.cedente_id
    if filters.payment_currency_code is not None:
        conditions.append("pc.code = :payment_currency_code")
        params["payment_currency_code"] = filters.payment_currency_code.upper()
    if filters.status is not None:
        conditions.append("t.status = :status")
        params["status"] = filters.status

    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where_sql, params


async def count(session: AsyncSession, filters: StatementFilters) -> int:
    where_sql, params = _build_where(filters)
    sql = f"""
        SELECT COUNT(*)
        FROM transactions t
        JOIN cedentes c ON c.id = t.cedente_id
        JOIN receivable_types rt ON rt.id = t.receivable_type_id
        JOIN currencies cur ON cur.id = t.currency_id
        JOIN currencies pc ON pc.id = t.payment_currency_id
        {where_sql}
    """
    result = await session.execute(text(sql), params)
    return int(result.scalar_one())


async def list_paginated(
    session: AsyncSession,
    filters: StatementFilters,
    page: int,
    page_size: int,
) -> list[StatementItem]:
    where_sql, params = _build_where(filters)
    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    sql = f"""
        SELECT
            t.id                 AS id,
            t.created_at         AS created_at,
            c.name               AS cedente_name,
            c.document           AS cedente_document,
            rt.name              AS receivable_type,
            t.face_value         AS face_value,
            t.present_value      AS present_value,
            cur.code             AS currency_code,
            pc.code              AS payment_currency_code,
            t.exchange_rate_used AS exchange_rate_used,
            t.status             AS status
        FROM transactions t
        JOIN cedentes c ON c.id = t.cedente_id
        JOIN receivable_types rt ON rt.id = t.receivable_type_id
        JOIN currencies cur ON cur.id = t.currency_id
        JOIN currencies pc ON pc.id = t.payment_currency_id
        {where_sql}
        ORDER BY t.created_at DESC
        LIMIT :limit OFFSET :offset
    """
    result = await session.execute(text(sql), params)
    return [StatementItem(**row) for row in result.mappings().all()]
