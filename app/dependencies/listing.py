"""Providers for the listing layer."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.db import SessionDep
from app.dependencies.hotel import HotelServiceDep
from app.dependencies.place import PlaceServiceDep
from app.repositories.listing import ListingRepository
from app.services.listing import ListingService


def get_listing_repository(session: SessionDep) -> ListingRepository:
    return ListingRepository(session)


ListingRepositoryDep = Annotated[ListingRepository, Depends(get_listing_repository)]


def get_listing_service(
    repository: ListingRepositoryDep,
    place_service: PlaceServiceDep,
    hotel_service: HotelServiceDep,
) -> ListingService:
    """Composes the place and hotel services so their rules are reused, not copied."""
    return ListingService(repository, place_service, hotel_service)


ListingServiceDep = Annotated[ListingService, Depends(get_listing_service)]
