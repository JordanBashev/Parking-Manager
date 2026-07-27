"""Declarative base and the building blocks every table reuses."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

UUID_LENGTH = 36


class Base(DeclarativeBase):
    """Root of all ORM models; owns the metadata that create_all reads."""


class UUIDPrimaryKeyMixin:
    """uuid4 primary key, stored as text because SQLite has no UUID type."""

    id: Mapped[str] = mapped_column(
        String(UUID_LENGTH), primary_key=True, default=lambda: str(uuid.uuid4())
    )


def utc_now() -> datetime:
    """Server-side timestamp default; always timezone-aware UTC."""
    return datetime.now(UTC)
