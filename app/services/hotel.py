"""Hotel-list rules. All persistence goes through the repository."""

from app.db.models.hotel import Hotel
from app.repositories.hotel import HotelRepository
from app.schemas.hotel import HotelCreate, HotelUpdate


class HotelNotFoundError(Exception):
    """Raised when the requested hotel does not exist."""


class HotelNameTakenError(Exception):
    """Raised when a hotel name collides with an existing one."""


class HotelService:
    def __init__(self, repository: HotelRepository) -> None:
        self.repository = repository

    async def list_hotels(self, active_only: bool) -> list[Hotel]:
        """List hotels; the selection boxes ask for active ones only."""
        return await self.repository.list_all(active_only)

    async def get(self, hotel_id: str) -> Hotel:
        hotel = await self.repository.get_by_id(hotel_id)
        if hotel is None:
            raise HotelNotFoundError(hotel_id)
        return hotel

    async def create(self, payload: HotelCreate) -> Hotel:
        if await self.repository.exists_by_name(payload.name):
            raise HotelNameTakenError(payload.name)
        return await self.repository.create(payload.name)

    async def update(self, hotel_id: str, payload: HotelUpdate) -> Hotel:
        """Apply only the fields that were sent; a hotel is never deleted,
        it is deactivated with `active=False`."""
        hotel = await self.get(hotel_id)

        if payload.name is not None:
            if await self.repository.exists_by_name(payload.name, exclude_id=hotel_id):
                raise HotelNameTakenError(payload.name)
            hotel.name = payload.name

        if payload.active is not None:
            hotel.active = payload.active

        return await self.repository.save(hotel)
