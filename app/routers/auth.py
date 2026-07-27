"""Login, logout and 'who am I'. Public except for /me."""

from fastapi import APIRouter, HTTPException, Response, status

from app.config import get_settings
from app.constants import SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS
from app.dependencies.auth import AuthServiceDep, CurrentUser
from app.schemas.user import LoginRequest, UserRead
from app.security import sign_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserRead)
async def login(payload: LoginRequest, response: Response, service: AuthServiceDep):
    """Verify credentials and set the signed session cookie."""
    user = await service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=sign_session(user.id),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Clear the session cookie. Attributes must match the ones set at login,
    or the browser won't remove it cross-site."""
    settings = get_settings()
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser):
    """Return the signed-in account."""
    return user
