"""Liveness endpoint. Infrastructure, not a domain — no service behind it."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report that the app is running."""
    return {"status": "ok"}
