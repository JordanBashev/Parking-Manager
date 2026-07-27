"""Deny-by-default access control.

FastAPI concatenates dependency lists rather than replacing them, so an
app-level `Depends(current_user)` cannot be switched off for the login route.
A middleware with an explicit allowlist is the only way to get "everything is
protected unless named public".
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import PUBLIC_PATHS, SESSION_COOKIE_NAME
from app.security import read_session

UNAUTHENTICATED = JSONResponse(
    {"detail": "Not authenticated"}, status_code=status.HTTP_401_UNAUTHORIZED
)


def is_public(path: str) -> bool:
    """Login, health and the docs need no session; everything else does."""
    return path in PUBLIC_PATHS


class RequireSessionMiddleware(BaseHTTPMiddleware):
    """Reject any request to a non-public path that carries no valid session.

    This only proves the cookie is genuine; loading the user and checking their
    role stays in the `current_user` / `require_admin` dependencies.
    """

    async def dispatch(self, request: Request, call_next):
        if is_public(request.url.path):
            return await call_next(request)

        cookie = request.cookies.get(SESSION_COOKIE_NAME)
        if cookie is None or read_session(cookie) is None:
            return UNAUTHENTICATED

        return await call_next(request)
