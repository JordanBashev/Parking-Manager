"""Application entrypoint: builds the FastAPI app and wires the routers.

Serves the JSON API under /api and the `app_frontend/` static app at /. Serving
both from one origin makes the session cookie first-party, which is what lets it
survive in browsers that block third-party cookies (Safari, Firefox, Brave).
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.constants import API_PREFIX, FRONTEND_DIRECTORY
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

# The frontend is mounted last so every /api route above is matched first.
FRONTEND_ROOT = Path(__file__).resolve().parent.parent / FRONTEND_DIRECTORY
INDEX_FILE = FRONTEND_ROOT / "index.html"


@app.get("/{spa_path:path}", include_in_schema=False)
async def serve_frontend(spa_path: str) -> FileResponse:
    """Serve a static file when one exists, else the SPA shell.

    The router uses real paths (/place/<id>), so a refresh or a shared deep link
    asks the server for a route that is not a file. Returning index.html lets the
    client-side router resolve it, instead of a 404.
    """
    candidate = (FRONTEND_ROOT / spa_path).resolve()
    # `..` segments must not escape the frontend folder and serve, say, .env.
    inside_frontend = candidate.is_relative_to(FRONTEND_ROOT)
    if spa_path and inside_frontend and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(INDEX_FILE)
