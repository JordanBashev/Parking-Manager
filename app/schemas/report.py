"""Request/response shapes for admin reports over archived data."""

from datetime import date, timedelta
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.fields import DisplayDate


class ReportFilters(BaseModel):
    """The filters an admin applies to a report. Every filter is optional and
    they combine with AND. Reports always cover archived places only."""

    date_from: DisplayDate | None = Field(
        default=None, description="Include listings recorded on or after this day (dd/mm/yyyy)."
    )
    date_to: DisplayDate | None = Field(
        default=None, description="Include listings recorded on or before this day (dd/mm/yyyy)."
    )
    hotel_id: str | None = Field(default=None, description="Limit to a single hotel.")
    worker: str | None = Field(default=None, description="Limit to a single worker's places.")

    @computed_field
    @property
    def date_to_exclusive(self) -> date | None:
        """`date_to` is inclusive of the whole day, but `Listing.date` is a
        timestamp — so the query compares against the start of the next day."""
        return None if self.date_to is None else self.date_to + timedelta(days=1)


class ReportTotals(BaseModel):
    """The three aggregates, for the whole result or one group within it."""

    total_listings: int = Field(description="How many listings matched.")
    total_count: int = Field(description="Sum of the `count` field across matches.")
    total_price: Decimal = Field(description="Sum of `price` across matches; 0.00 if none.")


class HotelBreakdown(ReportTotals):
    hotel_id: str = Field(description="The hotel these totals are for.")
    hotel_name: str = Field(description="Name of that hotel.")
    entered_date: DisplayDate = Field(
        description="The day these listings were entered (dd/mm/yyyy). One hotel "
        "can appear on several dates — each is its own row."
    )


class WorkerBreakdown(ReportTotals):
    worker: str = Field(description="The worker these totals are for.")


class Report(ReportTotals):
    """Totals over the filtered set, plus the same totals grouped two ways."""

    model_config = ConfigDict(from_attributes=True)

    by_hotel: list[HotelBreakdown] = Field(description="Totals per hotel, highest price first.")
    by_worker: list[WorkerBreakdown] = Field(description="Totals per worker, highest price first.")
