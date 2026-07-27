"""Assembles an admin report from the aggregate queries."""

from datetime import date, datetime

from app.repositories.report import ReportRepository
from app.schemas.report import (
    HotelBreakdown,
    Report,
    ReportFilters,
    WorkerBreakdown,
)


def _to_date(value: object) -> date:
    """`func.date()` yields an ISO 'YYYY-MM-DD' string on SQLite; normalise it (and
    any datetime, for Postgres) to a plain date for the DisplayDate field."""
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    if isinstance(value, datetime):
        return value.date()
    return value


class ReportService:
    def __init__(self, repository: ReportRepository) -> None:
        self.repository = repository

    async def build(self, filters: ReportFilters) -> Report:
        """Run the totals and both groupings over the same filter set."""
        total_listings, total_count, total_price = await self.repository.totals(filters)

        by_hotel = [
            HotelBreakdown(
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                entered_date=_to_date(entered),
                total_listings=listings,
                total_count=count_total,
                total_price=price_total,
            )
            for hotel_id, hotel_name, entered, listings, count_total, price_total
            in await self.repository.by_hotel(filters)
        ]

        by_worker = [
            WorkerBreakdown(
                worker=worker,
                total_listings=listings,
                total_count=count_total,
                total_price=price_total,
            )
            for worker, listings, count_total, price_total
            in await self.repository.by_worker(filters)
        ]

        return Report(
            total_listings=total_listings,
            total_count=total_count,
            total_price=total_price,
            by_hotel=by_hotel,
            by_worker=by_worker,
        )
