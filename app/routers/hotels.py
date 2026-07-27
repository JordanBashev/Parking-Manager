"""The hotel list. Any signed-in user may read it; only admins may change it."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies.auth import require_admin
from app.dependencies.hotel import HotelServiceDep
from app.schemas.hotel import HotelCreate, HotelRead, HotelUpdate
from app.services.hotel import HotelNameTakenError, HotelNotFoundError

router = APIRouter(prefix="/hotels", tags=["hotels"])

admin_only = Depends(require_admin)


@router.get("", response_model=list[HotelRead])
async def list_hotels(
    service: HotelServiceDep,
    active_only: bool = Query(
        default=True, description="Only hotels still offered in the selection boxes."
    ),
):
    """List hotels for the selection boxes."""
    return await service.list_hotels(active_only)


@router.post(
    "", response_model=HotelRead, status_code=status.HTTP_201_CREATED,
    dependencies=[admin_only],
)
async def create_hotel(payload: HotelCreate, service: HotelServiceDep):
    """Add a hotel to the list."""
    try:
        return await service.create(payload)
    except HotelNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Hotel name already exists")


@router.patch("/{hotel_id}", response_model=HotelRead, dependencies=[admin_only])
async def update_hotel(hotel_id: str, payload: HotelUpdate, service: HotelServiceDep):
    """Rename a hotel, or deactivate it so it stops appearing in the boxes."""
    try:
        return await service.update(hotel_id, payload)
    except HotelNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hotel not found")
    except HotelNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Hotel name already exists")
