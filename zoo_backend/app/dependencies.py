from typing import AsyncGenerator
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in _get_db():
        yield session


def paginate(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of records to return"
    ),
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}
