"""Providers for the auth layer: repository, service, current user, role guards."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from app.constants import SESSION_COOKIE_NAME, Role
from app.db.models.user import User
from app.dependencies.db import SessionDep
from app.repositories.user import UserRepository
from app.security import read_session
from app.services.auth import AuthService


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_service(repository: UserRepositoryDep) -> AuthService:
    return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def current_user(
    repository: UserRepositoryDep,
    cookie: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> User:
    """Resolve the signed session cookie to a User, or fail with 401."""
    user_id = read_session(cookie) if cookie else None
    user = await repository.get_by_id(user_id) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


async def require_admin(user: CurrentUser) -> User:
    """Allow only admins through; an authenticated worker gets 403."""
    if user.role != Role.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
