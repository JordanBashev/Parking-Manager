"""Application entrypoint: builds the FastAPI app and wires the routers.

The app is a pure JSON API — the frontend is served standalone from `app_frontend/`.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.constants import API_PREFIX
from app.db.base import Base
from app.db.session import engine
from app.middleware import RequireSessionMiddleware
from app.routers import auth, health, hotels, listings, ocr, places, reports, users
from app.scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and start the archiving scheduler on startup; stop the
    scheduler and dispose the engine on shutdown.

    create_all never drops or alters existing tables; it is a stand-in until
    Alembic is introduced.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    scheduler = build_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await engine.dispose()


app = FastAPI(title="Managining", lifespan=lifespan)

# Deny by default: only the paths in PUBLIC_PATHS are reachable without a session.
app.add_middleware(RequireSessionMiddleware)

# CORS is added last so it runs FIRST (Starlette runs outermost-added-last): the
# preflight OPTIONS must be answered before the session middleware can reject it.
# allow_credentials lets the browser send the cross-origin session cookie, which
# forbids a wildcard origin — the exact frontend origin is named.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(hotels.router, prefix=API_PREFIX)
app.include_router(places.router, prefix=API_PREFIX)
app.include_router(listings.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(ocr.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
