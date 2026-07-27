"""Providers for the place layer."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.db import SessionDep
from app.repositories.place import PlaceRepository
from app.services.place import PlaceService


def get_place_repository(session: SessionDep) -> PlaceRepository:
    return PlaceRepository(session)


PlaceRepositoryDep = Annotated[PlaceRepository, Depends(get_place_repository)]


def get_place_service(repository: PlaceRepositoryDep) -> PlaceService:
    return PlaceService(repository)


PlaceServiceDep = Annotated[PlaceService, Depends(get_place_service)]
