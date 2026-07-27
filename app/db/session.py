"""Async engine and session factory. The request-scoped dependency lives in
`app.dependencies.db` — this module only builds the machinery."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.sql_echo)

# expire_on_commit=False keeps attributes readable after commit; the default would
# expire them and force a lazy reload, which is not possible under async.
session_factory = async_sessionmaker(engine, expire_on_commit=False)
