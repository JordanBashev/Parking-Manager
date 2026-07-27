"""The only module that queries the listings table.

Listings carry no permissions of their own — they are reached through their
place, and `PlaceService` decides who may see it.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.listing import Listing


class ListingRepository:
    """Persistence for Listing. Knows nothing about HTTP or Pydantic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, listing_id: str) -> Listing | None:
        return await self.session.get(Listing, listing_id)

    async def list_for_place(self, place_id: str) -> list[Listing]:
        result = await self.session.execute(
            select(Listing).where(Listing.place_id == place_id).order_by(Listing.date)
        )
        return list(result.scalars())

    async def create(self, place_id: str, **fields) -> Listing:
        listing = Listing(place_id=place_id, **fields)
        self.session.add(listing)
        await self.session.commit()
        return listing

    async def save(self, listing: Listing) -> Listing:
        """Persist changes made to an already-loaded listing."""
        await self.session.commit()
        return listing
