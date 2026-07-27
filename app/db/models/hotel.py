"""Hotels — the admin-managed list that drives the clickable boxes."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import HOTEL_NAME_MAX_LENGTH
from app.db.base import Base, UUIDPrimaryKeyMixin


class Hotel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "hotels"

    name: Mapped[str] = mapped_column(
        String(HOTEL_NAME_MAX_LENGTH), unique=True, index=True
    )
    # Hotels are never deleted — listings reference them forever. Deactivating
    # only removes the hotel from the selection boxes.
    active: Mapped[bool] = mapped_column(default=True, index=True)
