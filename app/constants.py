"""Values shared across the whole app. No layer-specific constants here."""

from enum import StrEnum


class Role(StrEnum):
    """Account role; decides what a user may see and do."""

    ADMIN = "admin"
    WORKER = "worker"


SESSION_COOKIE_NAME = "session"
SESSION_SALT = "managining.session"  # namespaces the signature to this cookie's purpose
SESSION_MAX_AGE_SECONDS = 7 * 24 * 60 * 60

# bcrypt only hashes the first 72 bytes; cap input so the rest is never
# silently ignored.
PASSWORD_MAX_LENGTH = 72

USERNAME_MAX_LENGTH = 50
FIRST_NAME_MAX_LENGTH = 50
PASSWORD_HASH_MAX_LENGTH = 255

HOTEL_NAME_MAX_LENGTH = 100
PLACE_NAME_MAX_LENGTH = 100
MODEL_MAX_LENGTH = 100
REG_NUMBER_MAX_LENGTH = 50

# Money is Decimal, never float — binary floats cannot represent values like
# 0.10 exactly and totals drift. Numeric(TOTAL_DIGITS, DECIMAL_PLACES) gives
# 2 digits after the point and 8 before it, i.e. up to 99,999,999.99.
PRICE_TOTAL_DIGITS = 10
PRICE_DECIMAL_PLACES = 2

# The API speaks dd/mm/yyyy in both directions; the DB column stays a real Date
# so range queries and sorting work correctly.
DATE_FORMAT = "%d/%m/%Y"

# Plate OCR: only the highest-confidence detection above this threshold is read,
# so a weak/spurious box never produces a bogus reg number.
PLATE_DETECTION_MIN_CONFIDENCE = 0.25

API_PREFIX = "/api"

# The only paths reachable without a session. Everything else is denied by
# default — see app.middleware.require_session.
PUBLIC_PATHS = frozenset(
    {
        f"{API_PREFIX}/health",
        f"{API_PREFIX}/auth/login",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)

# The frontend is served from this app, so the login page and its assets must be
# reachable without a session — otherwise nobody can reach the form to log in.
# Anything NOT under API_PREFIX is a static file or a client-side route, and both
# are safe to serve anonymously: they contain no data. Every /api/* path stays
# deny-by-default, so this widens what is *visible*, never what is *readable*.
FRONTEND_DIRECTORY = "app_frontend"

# Auto end-of-day archiving fires at midnight GMT (= UTC), matching the UTC
# timestamps in the DB so "end of day" never drifts with server timezone.
ARCHIVE_TIMEZONE = "GMT"
ARCHIVE_HOUR = 0
ARCHIVE_MINUTE = 0
