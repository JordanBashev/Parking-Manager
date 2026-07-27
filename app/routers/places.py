"""Places. Workers see only their own; admins see everything.

There is no delete route: archiving is the intended end state for a place.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.dependencies.auth import CurrentUser, require_admin
from app.dependencies.place import PlaceServiceDep
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate, PlaceWithListings
from app.services.place import PlaceArchivedError, PlaceNotFoundError

router = APIRouter(prefix="/places", tags=["places"])


class ArchiveAllResult(BaseModel):
    archived: int = Field(description="How many open places were archived.")

PLACE_NOT_FOUND = "Place not found"
PLACE_ARCHIVED = "Place is archived and read-only"


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def create_place(payload: PlaceCreate, user: CurrentUser, service: PlaceServiceDep):
    """Create a place; `worker` and `date` are filled in server-side."""
    return await service.create(payload, user)


@router.get("", response_model=list[PlaceRead])
async def list_places(
    user: CurrentUser,
    service: PlaceServiceDep,
    archived: bool = Query(
        default=False, description="List archived places instead of open ones (admin only)."
    ),
):
    """List places, newest first."""
    return await service.list_places(user, archived)


@router.get("/{place_id}", response_model=PlaceWithListings)
async def get_place(place_id: str, user: CurrentUser, service: PlaceServiceDep):
    """Fetch one place together with its listings."""
    try:
        return await service.get_with_listings(place_id, user)
    except PlaceNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PLACE_NOT_FOUND)


@router.patch("/{place_id}", response_model=PlaceRead)
async def update_place(
    place_id: str, payload: PlaceUpdate, user: CurrentUser, service: PlaceServiceDep
):
    """Rename an open place."""
    try:
        return await service.update(place_id, payload, user)
    except PlaceNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PLACE_NOT_FOUND)
    except PlaceArchivedError:
        raise HTTPException(status.HTTP_409_CONFLICT, PLACE_ARCHIVED)


@router.post(
    "/archive-all", response_model=ArchiveAllResult, dependencies=[Depends(require_admin)]
)
async def archive_all_places(service: PlaceServiceDep):
    """TESTING/OPS ONLY: run the end-of-day archiving now, the same action the
    midnight scheduler performs. Archives every open place."""
    return ArchiveAllResult(archived=await service.archive_all_open())


@router.post("/{place_id}/archive", response_model=PlaceRead)
async def archive_place(place_id: str, user: CurrentUser, service: PlaceServiceDep):
    """Archive a place once its day is done. This cannot be undone."""
    try:
        return await service.archive(place_id, user)
    except PlaceNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PLACE_NOT_FOUND)
    except PlaceArchivedError:
        raise HTTPException(status.HTTP_409_CONFLICT, PLACE_ARCHIVED)
