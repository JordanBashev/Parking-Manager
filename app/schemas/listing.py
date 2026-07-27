"""Request/response shapes for listings."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants import MODEL_MAX_LENGTH, REG_NUMBER_MAX_LENGTH
from app.schemas.fields import DisplayDate


class ListingCreate(BaseModel):
    """A listing being entered against an open place.

    `place_id` comes from the URL and `date` is server-set, so neither appears
    here. Mistakes are fixed by editing — listings are never deleted.
    """

    hotel_id: str = Field(description="Id of the hotel box that was clicked; must be active.")
    model: str = Field(
        min_length=1, max_length=MODEL_MAX_LENGTH, description="Model of the item recorded."
    )
    reg_number: str = Field(
        min_length=1,
        max_length=REG_NUMBER_MAX_LENGTH,
        description="Registration number of the item.",
    )
    end_date: DisplayDate = Field(description="User-selected end date, as dd/mm/yyyy.")
    count: int | None = Field(
        default=None, ge=0, description="Quantity; may be filled in later."
    )
    price: Decimal | None = Field(
        default=None, ge=0, description="Money value; may be filled in later."
    )


class ListingUpdate(BaseModel):
    """Fields that may be corrected. Omitted fields are left untouched."""

    hotel_id: str | None = Field(default=None, description="Move the listing to another hotel.")
    model: str | None = Field(default=None, min_length=1, max_length=MODEL_MAX_LENGTH)
    reg_number: str | None = Field(
        default=None, min_length=1, max_length=REG_NUMBER_MAX_LENGTH
    )
    end_date: DisplayDate | None = Field(default=None, description="New end date, dd/mm/yyyy.")
    count: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0)


class ListingRead(BaseModel):
    """A listing as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="uuid4 primary key.")
    place_id: str = Field(description="The place this listing belongs to.")
    hotel_id: str = Field(description="The chosen hotel, referenced by id rather than name.")
    model: str = Field(max_length=MODEL_MAX_LENGTH, description="Model of the item recorded.")
    reg_number: str = Field(
        max_length=REG_NUMBER_MAX_LENGTH, description="Registration number of the item."
    )
    date: datetime = Field(description="UTC timestamp of when the listing was created.")
    end_date: DisplayDate | None = Field(
        description="User-selected end date, exchanged as dd/mm/yyyy."
    )
    count: int | None = Field(description="Quantity; meaning still being settled.")
    price: Decimal | None = Field(description="Money value; Decimal, never float.")
