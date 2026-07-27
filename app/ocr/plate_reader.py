"""Read a licence-plate registration number from a vehicle photo.

Infrastructure, not a domain service (it persists nothing and has no repository)
— it sits beside `security.py`. Two stages: a YOLOv8 model detects where the
plate is, then RapidOCR reads text from that crop. Both heavy objects are loaded
once, lazily, and reused.

Runs CPU-bound, blocking work — callers must invoke `read_plate` off the event
loop (e.g. `asyncio.to_thread`).
"""

import io
import re
from pathlib import Path

from PIL import Image

from app.constants import PLATE_DETECTION_MIN_CONFIDENCE

MODEL_PATH = Path(__file__).parent / "models" / "plate_detector.pt"

# A reg number is uppercase letters, digits and single spaces. Any other
# character (dashes, dots, stray symbols) is dropped, and runs of whitespace are
# collapsed to one space.
_NON_PLATE = re.compile(r"[^A-Z0-9 ]")
_MULTISPACE = re.compile(r"\s+")

# Only text at least this tall (relative to the biggest line on the plate) is
# kept. The registration characters are the large text; country codes and the
# tiny embossed stamps are much shorter and get discarded.
LARGE_TEXT_RATIO = 0.55

_detector = None
_reader = None


def _load_detector():
    """Load the YOLOv8 plate detector once and keep it in memory."""
    global _detector
    if _detector is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Plate detector model missing at {MODEL_PATH}. "
                "Download best.pt from the model repo and place it there."
            )
        from ultralytics import YOLO

        _detector = YOLO(str(MODEL_PATH))
    return _detector


def _load_reader():
    """Load the RapidOCR reader once and keep it in memory."""
    global _reader
    if _reader is None:
        from rapidocr_onnxruntime import RapidOCR

        _reader = RapidOCR()
    return _reader


def _best_plate_box(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Return the highest-confidence plate box, or None if none is confident."""
    results = _load_detector().predict(image, verbose=False)
    best_box = None
    best_confidence = PLATE_DETECTION_MIN_CONFIDENCE
    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])
            if confidence >= best_confidence:
                best_confidence = confidence
                left, top, right, bottom = (int(value) for value in box.xyxy[0])
                best_box = (left, top, right, bottom)
    return best_box


def _read_text(crop: Image.Image) -> str | None:
    """Run OCR on the plate crop and return the registration number.

    RapidOCR reads every text region on the plate — the large registration
    characters plus tiny stamps (country code, maker marks, embossed serials).
    Only the large text is the reg number, so detections shorter than
    LARGE_TEXT_RATIO of the tallest are dropped, and the survivors are joined in
    reading order (top-to-bottom, then left-to-right).
    """
    import numpy as np

    detections = _load_reader()(np.array(crop))[0]
    if not detections:
        return None

    def top(box):
        return min(point[1] for point in box)

    def left(box):
        return min(point[0] for point in box)

    def height(box):
        return max(point[1] for point in box) - top(box)

    tallest = max(height(box) for box, _, _ in detections)
    large = [
        (box, line_text)
        for box, line_text, _ in detections
        if height(box) >= tallest * LARGE_TEXT_RATIO
    ]
    # These plates are a single horizontal line, so read strictly left-to-right.
    large.sort(key=lambda item: left(item[0]))

    joined = " ".join(line_text for _, line_text in large).upper()
    cleaned = _MULTISPACE.sub(" ", _NON_PLATE.sub("", joined)).strip()
    return cleaned or None


def read_plate(image_bytes: bytes) -> str | None:
    """Return the plate's registration number, or None if it can't be read.

    A None result is normal (blurry photo, no plate in frame); the caller
    surfaces it so the user types the number in by hand.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    box = _best_plate_box(image)
    if box is None:
        return None
    return _read_text(image.crop(box))
