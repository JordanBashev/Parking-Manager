"""Request/response shapes for the admin-managed hotel list."""

from pydantic import BaseModel, ConfigDict, Field

from app.constants import HOTEL_NAME_MAX_LENGTH


class HotelCreate(BaseModel):
    """A hotel an admin is adding to the list."""

    name: str = Field(
        min_length=1,
        max_length=HOTEL_NAME_MAX_LENGTH,
        description="Display name shown on the clickable box; must be unique.",
    )


class HotelUpdate(BaseModel):
    """Fields an admin may change. Omitted fields are left untouched."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=HOTEL_NAME_MAX_LENGTH,
        description="New display name; must stay unique.",
    )
    active: bool | None = Field(
        default=None,
        description="False hides the hotel from the selection boxes without deleting it.",
    )


class HotelRead(BaseModel):
    """A hotel as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="uuid4 primary key; listings reference this, not the name.")
    name: str = Field(description="Display name shown on the clickable box.")
    active: bool = Field(
        description="Whether the hotel still appears when adding a listing."
    )
