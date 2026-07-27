"""Listings — the individual entries recorded against a Place."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import (
    MODEL_MAX_LENGTH,
    PRICE_DECIMAL_PLACES,
    PRICE_TOTAL_DIGITS,
    REG_NUMBER_MAX_LENGTH,
)
from app.db.base import UUID_LENGTH, Base, UUIDPrimaryKeyMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.hotel import Hotel
    from app.db.models.place import Place


class Listing(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "listings"

    place_id: Mapped[str] = mapped_column(
        String(UUID_LENGTH), ForeignKey("places.id"), index=True
    )
    hotel_id: Mapped[str] = mapped_column(
        String(UUID_LENGTH), ForeignKey("hotels.id"), index=True
    )
    model: Mapped[str] = mapped_column(String(MODEL_MAX_LENGTH))
    reg_number: Mapped[str] = mapped_column(String(REG_NUMBER_MAX_LENGTH), index=True)
    # Indexed: admin reports range-filter listings on this.
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    # User-selected; the API exchanges it as dd/mm/yyyy but stores a real Date.
    end_date: Mapped[date | None] = mapped_column(Date)
    # Meaning still TBD — kept nullable until the rules are settled.
    count: Mapped[int | None]
    price: Mapped[Decimal | None] = mapped_column(
        Numeric(PRICE_TOTAL_DIGITS, PRICE_DECIMAL_PLACES)
    )

    place: Mapped["Place"] = relationship(back_populates="listings")
    hotel: Mapped["Hotel"] = relationship()
