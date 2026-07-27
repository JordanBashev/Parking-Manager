"""Listing entry rules.

Listings have no permissions of their own: every operation resolves the parent
place through `PlaceService` first, so the ownership and archived rules are
defined once rather than duplicated here.
"""

from app.db.models.listing import Listing
from app.db.models.place import Place
from app.db.models.user import User
from app.repositories.listing import ListingRepository
from app.schemas.listing import ListingCreate, ListingUpdate
from app.services.hotel import HotelNotFoundError, HotelService
from app.services.place import PlaceArchivedError, PlaceService


class ListingNotFoundError(Exception):
    """Raised when a listing does not exist, or its place is not visible."""


class InactiveHotelError(Exception):
    """Raised when a listing points at a missing or deactivated hotel."""


class ListingService:
    def __init__(
        self,
        repository: ListingRepository,
        place_service: PlaceService,
        hotel_service: HotelService,
    ) -> None:
        self.repository = repository
        self.place_service = place_service
        self.hotel_service = hotel_service

    async def _writable_place(self, place_id: str, user: User) -> Place:
        """Return the place only if the user may see it and it is still open."""
        place = await self.place_service.get(place_id, user)
        if place.archived:
            raise PlaceArchivedError(place_id)
        return place

    async def _require_active_hotel(self, hotel_id: str) -> None:
        """A listing may only point at a hotel still offered in the boxes."""
        try:
            hotel = await self.hotel_service.get(hotel_id)
        except HotelNotFoundError as error:
            raise InactiveHotelError(hotel_id) from error
        if not hotel.active:
            raise InactiveHotelError(hotel_id)

    async def _visible_listing(self, listing_id: str, user: User) -> Listing:
        listing = await self.repository.get_by_id(listing_id)
        if listing is None:
            raise ListingNotFoundError(listing_id)
        # Resolving the place applies its 404 rules to the listing too.
        await self.place_service.get(listing.place_id, user)
        return listing

    async def list_for_place(self, place_id: str, user: User) -> list[Listing]:
        """List a place's listings; archived places stay readable for admins."""
        await self.place_service.get(place_id, user)
        return await self.repository.list_for_place(place_id)

    async def create(self, place_id: str, payload: ListingCreate, user: User) -> Listing:
        await self._writable_place(place_id, user)
        await self._require_active_hotel(payload.hotel_id)
        return await self.repository.create(place_id=place_id, **payload.model_dump())

    async def update(self, listing_id: str, payload: ListingUpdate, user: User) -> Listing:
        """Correct a listing. Mistakes are edited, never deleted."""
        listing = await self._visible_listing(listing_id, user)
        await self._writable_place(listing.place_id, user)

        changes = payload.model_dump(exclude_unset=True)
        if "hotel_id" in changes:
            await self._require_active_hotel(changes["hotel_id"])

        for field, value in changes.items():
            setattr(listing, field, value)

        return await self.repository.save(listing)
