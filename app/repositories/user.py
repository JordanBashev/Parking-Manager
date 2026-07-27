"""The only module that queries the users table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Role
from app.db.models.user import User


class UserRepository:
    """Persistence for User. Knows nothing about HTTP or Pydantic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def exists_by_username(self, username: str) -> bool:
        """Existence check that selects one id instead of loading the row."""
        result = await self.session.execute(
            select(User.id).where(User.username == username).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created))
        return list(result.scalars())

    async def create(
        self, username: str, first_name: str, password_hash: str, role: Role
    ) -> User:
        user = User(
            username=username,
            first_name=first_name,
            password_hash=password_hash,
            role=role,
        )
        self.session.add(user)
        await self.session.commit()
        return user
