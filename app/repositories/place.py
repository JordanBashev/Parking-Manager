"""The only module that queries the places table.

Every read takes an `owner_id` filter: `None` means unrestricted (admins only).
There is deliberately no unscoped query method, so a caller cannot forget to
scope one by accident.
"""

from datetime import datetime

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.listing import Listing
from app.db.models.place import Place


class PlaceRepository:
    """Persistence for Place. Knows nothing about HTTP or Pydantic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _scoped(query: Select, owner_id: str | None) -> Select:
        """Restrict a query to one owner's rows; None leaves it unrestricted."""
        return query if owner_id is None else query.where(Place.created_by == owner_id)

    async def get(self, place_id: str, owner_id: str | None) -> Place | None:
        query = self._scoped(select(Place).where(Place.id == place_id), owner_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_listings(self, place_id: str, owner_id: str | None) -> Place | None:
        """Load a place and its listings in two queries rather than N+1."""
        query = self._scoped(
            select(Place).options(selectinload(Place.listings)).where(Place.id == place_id),
            owner_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_places(
        self, owner_id: str | None, archived: bool
    ) -> list[tuple[Place, int]]:
        """Return each place with its listing count in one query.

        The count is a correlated scalar subquery, so there is no N+1 — one row
        per place already carries its total.
        """
        listing_count = (
            select(func.count(Listing.id))
            .where(Listing.place_id == Place.id)
            .correlate(Place)
            .scalar_subquery()
        )
        query = self._scoped(
            select(Place, listing_count)
            .where(Place.archived.is_(archived))
            .order_by(Place.date.desc()),
            owner_id,
        )
        result = await self.session.execute(query)
        return [(place, count) for place, count in result.all()]

    async def create(self, name: str, worker: str, created_by: str) -> Place:
        place = Place(name=name, worker=worker, created_by=created_by)
        self.session.add(place)
        await self.session.commit()
        return place

    async def save(self, place: Place) -> Place:
        """Persist changes made to an already-loaded place."""
        await self.session.commit()
        return place

    async def archive(self, place: Place, archived_at: datetime) -> Place:
        place.archived = True
        place.archived_at = archived_at
        return await self.save(place)

    async def archive_all_open(self, archived_at: datetime) -> int:
        """Archive every open place in one UPDATE; returns how many were changed.

        A system action, not a user action — deliberately unscoped by owner.
        """
        result = await self.session.execute(
            update(Place)
            .where(Place.archived.is_(False))
            .values(archived=True, archived_at=archived_at)
        )
        await self.session.commit()
        return result.rowcount
