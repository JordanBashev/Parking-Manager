"""User accounts. Created by admins only — there is no open registration."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import (
    FIRST_NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    Role,
)
from app.db.base import Base, UUIDPrimaryKeyMixin, utc_now


class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    # Login identifier; indexed because every login filters on it.
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), unique=True, index=True
    )
    # Copied onto each Place this user creates, as its "worker".
    first_name: Mapped[str] = mapped_column(String(FIRST_NAME_MAX_LENGTH))
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH))
    # values_callable stores the enum's value ("admin"), not its name ("ADMIN").
    role: Mapped[Role] = mapped_column(
        Enum(Role, native_enum=False, values_callable=lambda enum: [item.value for item in enum])
    )
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
