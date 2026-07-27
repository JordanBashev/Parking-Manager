"""Plate OCR. Upload a vehicle photo, get back the registration number to
pre-fill the listing form. Reads nothing from and writes nothing to the DB."""

import asyncio

from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.dependencies.auth import CurrentUser
from app.ocr.plate_reader import read_plate

router = APIRouter(prefix="/ocr", tags=["ocr"])

MODEL_UNAVAILABLE = "Plate reader is not available on the server."


class PlateRead(BaseModel):
    reg_number: str | None = Field(
        description="The plate's registration number, or null if it couldn't be read."
    )


@router.post("/plate", response_model=PlateRead)
async def read_plate_from_photo(image: UploadFile, user: CurrentUser):
    """Detect and read a licence plate from an uploaded photo.

    The model work is CPU-bound and blocking, so it runs in a worker thread to
    keep the event loop free. A null result means the user types it in manually.
    """
    image_bytes = await image.read()
    try:
        reg_number = await asyncio.to_thread(read_plate, image_bytes)
    except FileNotFoundError:
        # The detector model isn't on the server — an ops problem, not a bad request.
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, MODEL_UNAVAILABLE)
    return PlateRead(reg_number=reg_number)
