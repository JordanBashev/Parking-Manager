"""Reusable field types shared by schemas.

Keeps the dd/mm/yyyy convention defined once instead of repeated per schema.
"""

from datetime import date, datetime
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

from app.constants import DATE_FORMAT


def parse_display_date(value: object) -> object:
    """Accept a dd/mm/yyyy string (API input) or a datetime read from the DB;
    leave anything else for Pydantic to handle.

    SQLite returns naive datetimes for the server-set timestamp columns, so
    narrowing datetime → date here lets those columns serialize as dd/mm/yyyy.
    """
    if isinstance(value, str):
        return datetime.strptime(value.strip(), DATE_FORMAT).date()
    if isinstance(value, datetime):
        return value.date()
    return value


# A date the API reads and writes as dd/mm/yyyy while the DB keeps a real Date.
#
# when_used="json" is essential: without it the serializer also fires on
# `model_dump()`, which services use to build ORM objects, and a display string
# would be handed to a SQL Date column.
DisplayDate = Annotated[
    date,
    BeforeValidator(parse_display_date),
    PlainSerializer(
        lambda value: value.strftime(DATE_FORMAT), return_type=str, when_used="json"
    ),
]
