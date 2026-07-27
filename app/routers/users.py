"""Admin-only account management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import AuthServiceDep, require_admin
from app.schemas.user import UserCreate, UserRead
from app.services.auth import UsernameTakenError

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: AuthServiceDep):
    """Create a worker account. Admins are only made by the seed CLI."""
    try:
        return await service.create_worker(payload)
    except UsernameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")


@router.get("", response_model=list[UserRead])
async def list_users(service: AuthServiceDep):
    """List every account."""
    return await service.list_users()
