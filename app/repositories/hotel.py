"""The only module that queries the hotels table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.hotel import Hotel


class HotelRepository:
    """Persistence for Hotel. Knows nothing about HTTP or Pydantic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, hotel_id: str) -> Hotel | None:
        return await self.session.get(Hotel, hotel_id)

    async def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool:
        """Existence check that selects one id instead of loading the row.

        `exclude_id` lets a rename ignore the row being renamed.
        """
        query = select(Hotel.id).where(Hotel.name == name)
        if exclude_id is not None:
            query = query.where(Hotel.id != exclude_id)
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    async def list_all(self, active_only: bool) -> list[Hotel]:
        query = select(Hotel).order_by(Hotel.name)
        if active_only:
            query = query.where(Hotel.active.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars())

    async def create(self, name: str) -> Hotel:
        hotel = Hotel(name=name)
        self.session.add(hotel)
        await self.session.commit()
        return hotel

    async def save(self, hotel: Hotel) -> Hotel:
        """Persist changes made to an already-loaded hotel."""
        await self.session.commit()
        return hotel
