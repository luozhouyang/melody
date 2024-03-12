import abc
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .tables import User


class AbstractUserService(abc.ABC):
    """Abstract user service"""

    @abc.abstractmethod
    async def fetch(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by id

        :param user_id: The id of the user
        :return: The user, or None if not found
        """
        pass

    @abc.abstractmethod
    async def save(self, user: User) -> User:
        """Create or update a user

        :param user: The user to create or update
        :return: The user
        """
        pass

    @abc.abstractmethod
    async def delete(self, user_id: uuid.UUID, soft_delete: bool = True, **kwargs) -> Optional[User]:
        """Delete a user

        :param user_id: The id of the user to delete
        :param soft_delete: Whether to soft delete the user, if True set deleted_at to now, if False, delete the record
        :return: The user that was deleted, or None if not exist
        """
        pass


class DefaultUserService(AbstractUserService):
    """Default user service implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch(self, user_id: uuid.UUID) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        return await self.session.scalar(query)

    async def save(self, user: User) -> User:
        if not user:
            raise ValueError("User cannot be None")
        if not user.id:
            raise ValueError("User id cannot be None")
        exit = await self.session.scalar(select(User).where(User.id == user.id))
        if exit:
            # do update
            exit.updated_at = datetime.utcnow()
            for k, v in user.model_dump().items():
                if v is not None:
                    setattr(exit, k, v)
            self.session.add(exit)
            return exit
        # do insert
        utc_now = datetime.utcnow()
        if not user.created_at:
            user.created_at = utc_now
        if not user.updated_at:
            user.updated_at = utc_now
        user.deleted_at = None
        self.session.add(user)

    async def delete(self, user_id: uuid.UUID, soft_delete: bool = True, **kwargs) -> Optional[User]:
        stat = select(User).where(User.id == user_id)
        user = await self.session.scalar(stat)
        if not user:
            return None
        if not soft_delete:
            self.session.delete(user)
            return user

        user.deleted_at = datetime.utcnow()
        self.session.add(user)
        return user
