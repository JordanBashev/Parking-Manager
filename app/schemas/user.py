"""Request/response shapes for accounts and login."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import (
    FIRST_NAME_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    Role,
)


class LoginRequest(BaseModel):
    """Credentials submitted by the login page."""

    username: str = Field(description="The account's login identifier.")
    password: str = Field(
        max_length=PASSWORD_MAX_LENGTH,
        description="Plaintext password, checked against the stored hash.",
    )


class UserCreate(BaseModel):
    """An account an admin is creating. Only workers can be created in-app —
    further admins are made by the seed CLI."""

    username: str = Field(
        max_length=USERNAME_MAX_LENGTH,
        description="Unique login identifier; rejected if already taken.",
    )
    first_name: str = Field(
        max_length=FIRST_NAME_MAX_LENGTH,
        description="Auto-filled as the 'worker' on every Place this user creates.",
    )
    password: str = Field(
        max_length=PASSWORD_MAX_LENGTH,
        description="Initial password, hashed before storage. Capped at bcrypt's 72-byte limit.",
    )


class UserRead(BaseModel):
    """An account as returned by the API. Never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="uuid4 primary key.")
    username: str = Field(description="The account's login identifier.")
    first_name: str = Field(description="Used as the 'worker' name on the user's Places.")
    role: Role = Field(description="'admin' sees everything; 'worker' sees only their own.")
    created: datetime = Field(description="UTC timestamp of when the account was made.")
