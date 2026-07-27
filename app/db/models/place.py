"""Places — a named day's work, owned by the user who created it."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import FIRST_NAME_MAX_LENGTH, PLACE_NAME_MAX_LENGTH
from app.db.base import UUID_LENGTH, Base, UUIDPrimaryKeyMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.listing import Listing


class Place(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String(PLACE_NAME_MAX_LENGTH))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    # A snapshot of the creator's first name, deliberately copied rather than
    # joined: renaming a user must not rewrite history on their past places.
    worker: Mapped[str] = mapped_column(String(FIRST_NAME_MAX_LENGTH))
    created_by: Mapped[str] = mapped_column(
        String(UUID_LENGTH), ForeignKey("users.id"), index=True
    )
    # Archived places are admin-only and read-only.
    archived: Mapped[bool] = mapped_column(default=False, index=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    listings: Mapped[list["Listing"]] = relationship(
        back_populates="place", cascade="all, delete-orphan"
    )
