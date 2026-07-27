"""Auto end-of-day archiving.

A daily cron job at midnight GMT archives every place still open. It runs
outside any request, so it builds its own session and PlaceService rather than
using request dependencies, and calls the same `archive_all_open` the manual
test button uses.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.constants import ARCHIVE_HOUR, ARCHIVE_MINUTE, ARCHIVE_TIMEZONE
from app.db.session import session_factory
from app.repositories.place import PlaceRepository
from app.services.place import PlaceService

logger = logging.getLogger(__name__)


async def archive_open_places() -> None:
    """The scheduled job: close every open place for the day."""
    async with session_factory() as session:
        service = PlaceService(PlaceRepository(session))
        archived = await service.archive_all_open()
    logger.info("End-of-day archiving ran: %d place(s) archived.", archived)


def build_scheduler() -> AsyncIOScheduler:
    """Create the scheduler with the daily archiving job registered."""
    scheduler = AsyncIOScheduler(timezone=ARCHIVE_TIMEZONE)
    scheduler.add_job(
        archive_open_places,
        CronTrigger(
            hour=ARCHIVE_HOUR, minute=ARCHIVE_MINUTE, timezone=ARCHIVE_TIMEZONE
        ),
        id="end_of_day_archiving",
        replace_existing=True,
    )
    return scheduler
