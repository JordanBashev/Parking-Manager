"""Providers for the hotel layer."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.db import SessionDep
from app.repositories.hotel import HotelRepository
from app.services.hotel import HotelService


def get_hotel_repository(session: SessionDep) -> HotelRepository:
    return HotelRepository(session)


HotelRepositoryDep = Annotated[HotelRepository, Depends(get_hotel_repository)]


def get_hotel_service(repository: HotelRepositoryDep) -> HotelService:
    return HotelService(repository)


HotelServiceDep = Annotated[HotelService, Depends(get_hotel_service)]
