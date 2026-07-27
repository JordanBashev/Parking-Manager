"""Login and account-creation rules. All persistence goes through the repository."""

from app.constants import Role
from app.db.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password


class UsernameTakenError(Exception):
    """Raised when an account is created with a username that already exists."""


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def authenticate(self, username: str, password: str) -> User | None:
        """Return the user if the credentials match, else None."""
        user = await self.repository.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user

    async def create_worker(self, payload: UserCreate) -> User:
        """Create a worker account. Admins are only made by the seed CLI."""
        if await self.repository.exists_by_username(payload.username):
            raise UsernameTakenError(payload.username)
        return await self.repository.create(
            username=payload.username,
            first_name=payload.first_name,
            password_hash=hash_password(payload.password),
            role=Role.WORKER,
        )

    async def list_users(self) -> list[User]:
        return await self.repository.list_all()
