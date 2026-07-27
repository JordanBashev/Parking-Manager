"""Importing every model here keeps `Base.metadata` complete for create_all."""

from app.db.models.hotel import Hotel
from app.db.models.listing import Listing
from app.db.models.place import Place
from app.db.models.user import User

__all__ = ["Hotel", "Listing", "Place", "User"]
