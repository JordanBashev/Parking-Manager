"""Listing entry. A listing is reached through its place, which decides access.

There is no delete route: a mistyped listing is corrected with PATCH.
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies.auth import CurrentUser
from app.dependencies.listing import ListingServiceDep
from app.schemas.listing import ListingCreate, ListingRead, ListingUpdate
from app.services.listing import InactiveHotelError, ListingNotFoundError
from app.services.place import PlaceArchivedError, PlaceNotFoundError

router = APIRouter(tags=["listings"])

LISTING_NOT_FOUND = "Listing not found"
PLACE_NOT_FOUND = "Place not found"
PLACE_ARCHIVED = "Place is archived and read-only"
INACTIVE_HOTEL = "Hotel does not exist or is no longer active"


@router.post(
    "/places/{place_id}/listings",
    response_model=ListingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_listing(
    place_id: str, payload: ListingCreate, user: CurrentUser, service: ListingServiceDep
):
    """Save a listing against an open place."""
    try:
        return await service.create(place_id, payload, user)
    except PlaceNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PLACE_NOT_FOUND)
    except PlaceArchivedError:
        raise HTTPException(status.HTTP_409_CONFLICT, PLACE_ARCHIVED)
    except InactiveHotelError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, INACTIVE_HOTEL)


@router.get("/places/{place_id}/listings", response_model=list[ListingRead])
async def list_listings(place_id: str, user: CurrentUser, service: ListingServiceDep):
    """List a place's listings, oldest first."""
    try:
        return await service.list_for_place(place_id, user)
    except PlaceNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PLACE_NOT_FOUND)


@router.patch("/listings/{listing_id}", response_model=ListingRead)
async def update_listing(
    listing_id: str, payload: ListingUpdate, user: CurrentUser, service: ListingServiceDep
):
    """Correct a listing while its place is still open."""
    try:
        return await service.update(listing_id, payload, user)
    except (ListingNotFoundError, PlaceNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, LISTING_NOT_FOUND)
    except PlaceArchivedError:
        raise HTTPException(status.HTTP_409_CONFLICT, PLACE_ARCHIVED)
    except InactiveHotelError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, INACTIVE_HOTEL)
