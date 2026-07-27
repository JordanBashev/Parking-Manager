"""Place rules: ownership visibility and archiving.

Archiving is terminal — a place is never un-archived and never deleted.
"""

from app.constants import Role
from app.db.base import utc_now
from app.db.models.place import Place
from app.db.models.user import User
from app.repositories.place import PlaceRepository
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate


class PlaceNotFoundError(Exception):
    """Raised when a place does not exist, or the user may not see it.

    Deliberately the same error for both: telling a worker that someone else's
    place exists would leak information they have no access to.
    """


class PlaceArchivedError(Exception):
    """Raised when a write is attempted against an archived (read-only) place."""


class PlaceService:
    def __init__(self, repository: PlaceRepository) -> None:
        self.repository = repository

    @staticmethod
    def _owner_filter(user: User) -> str | None:
        """Admins see every place; everyone else only their own."""
        return None if user.role == Role.ADMIN else user.id

    @staticmethod
    def _is_hidden(place: Place | None, user: User) -> bool:
        """Archived places are admin-only, so a worker must not see them at all."""
        return place is None or (place.archived and user.role != Role.ADMIN)

    async def create(self, payload: PlaceCreate, user: User) -> Place:
        """Create a place, snapshotting the creator's first name as its worker."""
        return await self.repository.create(
            name=payload.name, worker=user.first_name, created_by=user.id
        )

    async def list_places(self, user: User, archived: bool) -> list[PlaceRead]:
        """Return places as read schemas, each carrying its listing count."""
        if archived and user.role != Role.ADMIN:
            return []
        rows = await self.repository.list_places(self._owner_filter(user), archived)
        return [
            PlaceRead.model_validate(place).model_copy(update={"listing_count": count})
            for place, count in rows
        ]

    async def get(self, place_id: str, user: User) -> Place:
        place = await self.repository.get(place_id, self._owner_filter(user))
        if self._is_hidden(place, user):
            raise PlaceNotFoundError(place_id)
        return place

    async def get_with_listings(self, place_id: str, user: User) -> Place:
        place = await self.repository.get_with_listings(place_id, self._owner_filter(user))
        if self._is_hidden(place, user):
            raise PlaceNotFoundError(place_id)
        return place

    async def update(self, place_id: str, payload: PlaceUpdate, user: User) -> Place:
        """Rename an open place. Archived places are read-only, for admins too."""
        place = await self.get(place_id, user)
        if place.archived:
            raise PlaceArchivedError(place_id)

        if payload.name is not None:
            place.name = payload.name

        return await self.repository.save(place)

    async def archive(self, place_id: str, user: User) -> Place:
        """Close a place for the day. There is no way back."""
        place = await self.get(place_id, user)
        if place.archived:
            raise PlaceArchivedError(place_id)
        return await self.repository.archive(place, utc_now())

    async def archive_all_open(self) -> int:
        """Close every open place at end of day. Used by the scheduler and the
        manual test button; returns how many places were archived."""
        return await self.repository.archive_all_open(utc_now())
