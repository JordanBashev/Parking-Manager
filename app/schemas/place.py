"""Request/response shapes for places."""

from pydantic import BaseModel, ConfigDict, Field

from app.constants import PLACE_NAME_MAX_LENGTH
from app.schemas.fields import DisplayDate
from app.schemas.listing import ListingRead


class PlaceCreate(BaseModel):
    """A place the signed-in user is creating.

    Only the name is accepted: `worker`, `date` and `created_by` are set
    server-side from the session and are never trusted from the client.
    """

    name: str = Field(
        min_length=1,
        max_length=PLACE_NAME_MAX_LENGTH,
        description="What the place is called, e.g. 'Central'.",
    )


class PlaceUpdate(BaseModel):
    """Fields that may be changed while the place is still open."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=PLACE_NAME_MAX_LENGTH,
        description="New name for the place. Rejected once archived.",
    )


class PlaceRead(BaseModel):
    """A place as returned by the API, without its listings."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="uuid4 primary key.")
    name: str = Field(description="What the place is called, e.g. 'Central'.")
    date: DisplayDate = Field(description="Creation date, shown as dd/mm/yyyy.")
    worker: str = Field(
        description="First name of the creating user, snapshotted at creation."
    )
    created_by: str = Field(description="Id of the owning user; workers only see their own.")
    archived: bool = Field(
        description="Archived places are admin-only and can no longer be changed."
    )
    archived_at: DisplayDate | None = Field(
        description="Date the place was archived (dd/mm/yyyy); null while open."
    )
    listing_count: int = Field(
        default=0, description="How many listings this place holds."
    )


class PlaceWithListings(PlaceRead):
    """A place together with its listings, for the add-listings page."""

    listings: list[ListingRead] = Field(
        description="Every listing recorded against this place, oldest first."
    )
