"""Create the first admin account.

The only way an admin comes into being — the API can create workers only.
Run once on setup:  python seed_admin.py
"""

import asyncio
from getpass import getpass

from app.constants import PASSWORD_MAX_LENGTH, Role
from app.db.base import Base
from app.db.session import engine, session_factory
from app.repositories.user import UserRepository
from app.security import hash_password


async def seed_admin() -> None:
    username = input("Username: ").strip()
    first_name = input("First name: ").strip()
    password = getpass("Password: ")

    if not (username and first_name and password):
        raise SystemExit("Username, first name and password are all required.")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise SystemExit(f"Password must be at most {PASSWORD_MAX_LENGTH} characters.")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        repository = UserRepository(session)
        if await repository.exists_by_username(username):
            raise SystemExit(f"Username {username!r} is already taken.")
        await repository.create(
            username=username,
            first_name=first_name,
            password_hash=hash_password(password),
            role=Role.ADMIN,
        )

    await engine.dispose()
    print(f"Admin {username!r} created.")


if __name__ == "__main__":
    asyncio.run(seed_admin())
