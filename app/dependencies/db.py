"""Request-scoped database session provider."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one session per request; roll back on failure, always close."""
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
