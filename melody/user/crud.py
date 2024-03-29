import logging
import uuid

from sqlmodel import insert, select, update

from melody import utils
from melody.deps import database

from .models import UserCreateRequest, UserPatchRequest, UserUpdateRequest
from .tables import User

logger = logging.getLogger("melody.user")


@database.transaction()
async def create_user(request: UserCreateRequest) -> User:
    user = User()
    user.model_copy(update=request.model_dump())
    rows = await database.execute(insert(User), values=user.model_dump())
    logger.info(f"create user affected rows: {rows}")

    q = select(User).where(User.id == user.id)
    user: User = database.fetch_one(q)
    assert user is not None
    logger.debug(f"created user: {user.model_dump_json()}")
    return user


@database.transaction()
async def update_user(id: uuid.UUID, request: UserUpdateRequest) -> User | None:
    values = request.model_dump()
    values["updated_at"] = utils.utc_now()
    user: User = await database.execute(update(User).where(User.id == id).returning(User), values=values)
    if not user:
        logger.info(f"no user found by id: {id}, skipped.")
        return None
    logger.debug(f"updated user: {user.model_dump_json()}")
    return user


@database.transaction()
async def patch_user(id: uuid.UUID, request: UserPatchRequest) -> User | None:
    user: User = database.fetch_one(select(User).where(User.id == id))
    if not user:
        logger.info(f"no user found by id: {id}, skipped.")
        return None
    if request.props:
        user.props.update(request.props)
    user.model_copy(update=request.model_dump(exclude_unset=True))
    user.updated_at = utils.utc_now()
    rows = await database.execute(update(User).where(User.id == id), values=user.model_dump())
    logger.debug(f"patch user affected rows: {rows}")
    return user


@database.transaction()
async def delete_user(id: uuid.UUID) -> User | None:
    q = update(User).where(User.id == id).returning(User)
    user: User = await database.execute(q, values={"deleted_at": utils.utc_now()})
    if not user:
        logger.info(f"no user found by id: {id}, skipped.")
        return None
    logger.debug(f"deleted user: {user.model_dump_json()}")
    return user
