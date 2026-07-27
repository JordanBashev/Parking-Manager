"""The only module that queries listings for admin reports.

All aggregation happens in SQL — counts and sums are never computed by loading
rows into Python. Reports cover archived places only.
"""

from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.hotel import Hotel
from app.db.models.listing import Listing
from app.db.models.place import Place
from app.schemas.report import ReportFilters

# SUM over no rows is NULL; coalesce so the API always returns clean numbers.
_COUNT_SUM = func.coalesce(func.sum(Listing.count), 0)
_PRICE_SUM = func.coalesce(func.sum(Listing.price), 0)
_LISTINGS = func.count(Listing.id)


class ReportRepository:
    """Persistence for reports. Knows nothing about HTTP or Pydantic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _apply_filters(query: Select, filters: ReportFilters) -> Select:
        """Restrict a listings query to what the admin asked for.

        Archived-only is unconditional; every other filter is applied only when
        it was provided, and they combine with AND.
        """
        query = query.where(Place.archived.is_(True))
        if filters.date_from is not None:
            query = query.where(Listing.date >= filters.date_from)
        if filters.date_to_exclusive is not None:
            query = query.where(Listing.date < filters.date_to_exclusive)
        if filters.hotel_id is not None:
            query = query.where(Listing.hotel_id == filters.hotel_id)
        if filters.worker is not None:
            query = query.where(Place.worker == filters.worker)
        return query

    def _base(self, filters: ReportFilters) -> Select:
        """A filtered join of listings to their place, ready to aggregate."""
        return self._apply_filters(
            select(Listing).join(Place, Listing.place_id == Place.id), filters
        )

    async def totals(self, filters: ReportFilters) -> tuple[int, int, Decimal]:
        query = self._base(filters).with_only_columns(_LISTINGS, _COUNT_SUM, _PRICE_SUM)
        listings, count_total, price_total = (await self.session.execute(query)).one()
        return listings, count_total, Decimal(price_total)

    async def by_hotel(self, filters: ReportFilters) -> list[tuple]:
        """Group by hotel AND the day the listings were entered — one hotel can
        hold several dated batches, so each (hotel, date) is its own row."""
        entered = func.date(Listing.date)
        query = (
            self._base(filters)
            .join(Hotel, Listing.hotel_id == Hotel.id)
            .with_only_columns(
                Hotel.id, Hotel.name, entered, _LISTINGS, _COUNT_SUM, _PRICE_SUM
            )
            .group_by(Hotel.id, Hotel.name, entered)
            .order_by(_PRICE_SUM.desc())
        )
        return list(await self.session.execute(query))

    async def by_worker(self, filters: ReportFilters) -> list[tuple]:
        query = (
            self._base(filters)
            .with_only_columns(Place.worker, _LISTINGS, _COUNT_SUM, _PRICE_SUM)
            .group_by(Place.worker)
            .order_by(_PRICE_SUM.desc())
        )
        return list(await self.session.execute(query))
