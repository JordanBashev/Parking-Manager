"""Password hashing and session-cookie signing. Pure functions — no DB, no HTTP."""

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import get_settings
from app.constants import SESSION_MAX_AGE_SECONDS, SESSION_SALT

serializer = URLSafeTimedSerializer(get_settings().session_secret, salt=SESSION_SALT)


def hash_password(password: str) -> str:
    """Return a bcrypt hash; the plaintext is never stored anywhere.

    Input is capped at 72 characters by the schemas — bcrypt rejects anything
    longer rather than truncating it.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def sign_session(user_id: str) -> str:
    """Serialize a user id into a signed, timestamped cookie value.

    Signed, not encrypted: the id is readable by the client but cannot be
    altered without the session secret.
    """
    return serializer.dumps(user_id)


def read_session(cookie: str) -> str | None:
    """Return the user id, or None if the cookie is forged, corrupt or expired."""
    try:
        return serializer.loads(cookie, max_age=SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
