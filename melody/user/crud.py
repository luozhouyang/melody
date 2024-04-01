import logging
import uuid

from sqlmodel import delete, insert, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from melody import utils

from .models import UserCreateRequest, UserPatchRequest, UserUpdateRequest
from .tables import User

logger = logging.getLogger("melody.user")


async def retrieve_user(session: AsyncSession, *, id: uuid.UUID) -> User | None:
    sql = select(User).where(User.id == id)
    logger.debug(f"retrieving user sql: {sql}")
    user = await session.exec(sql).first()
    logger.debug(f"retrieved user: {user}")
    return user


async def create_user(session: AsyncSession, *, request: UserCreateRequest) -> User:
    user = User()
    user.model_copy(update=request.model_dump())
    sql = insert(User).values(user.model_dump())
    logger.debug(f"creating user sql: {sql}")
    user: User = await session.exec(sql).one()
    logger.debug(f"created user: {user}")
    return user


async def update_user(session: AsyncSession, *, id: uuid.UUID, request: UserUpdateRequest) -> User | None:
    values = request.model_dump()
    values["updated_at"] = utils.utc_now()
    sql = update(User).where(User.id == id).values(values).returning(User)
    user = await session.exec(sql).first()
    logger.debug(f"updated user: {user}")
    return user


async def patch_user(session: AsyncSession, *, id: uuid.UUID, request: UserPatchRequest) -> User | None:
    values = request.model_dump(exclude_unset=True)
    values["updated_at"] = utils.utc_now()
    sql = update(User).where(User.id == id).values(values).returning(User)
    logger.debug(f"patching user sql: {sql}")
    user = await session.exec(sql).first()
    return user


async def delete_user(session: AsyncSession, *, id: uuid.UUID, soft_delete: bool = False) -> User | None:
    if soft_delete:
        sql = update(User).where(User.id == id).values(deleted_at=utils.utc_now(), status="DELETED").returning(User)
    else:
        sql = delete(User).where(User.id == id).returning(User)
    logger.debug(f"deleting user sql: {sql}")
    user = session.exec(sql).first()
    logger.debug(f"deleted user: {user}")
    return user
