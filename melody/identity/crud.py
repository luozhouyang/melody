import logging
import uuid
from typing import List

import bcrypt
from sqlalchemy import delete, insert, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from melody import utils

from .models import (
    EmailIdentityCreateRequest,
    EmailIdentityPatchRequest,
    EmailIdentityResetPasswordRequest,
    EmailIdentityUpdateRequest,
    OAuth2IdentityCreateRequest,
    OAuth2IdentityPatchRequest,
    OAuth2IdentityUpdateRequest,
)
from .tables import Identity

logger = logging.getLogger("melody.identity")


async def retrieve_identity(session: AsyncSession, *, id: uuid.UUID) -> Identity | None:
    sql = select(Identity).where(Identity.id == id)
    logger.debug(f"retrieving identity sql: {sql}")
    identity = await session.exec(sql).first()
    logger.debug(f"retrieved identity: {identity}")
    return identity


async def retrieve_identities_by_user_id(session: AsyncSession, *, user_id: uuid.UUID) -> List[Identity] | None:
    sql = select(Identity).where(Identity.user_id == user_id)
    logger.debug(f"retrieving identity sql: {sql}")
    identities = await session.exec(sql).all()
    logger.debug(f"retrieved identity: {identities}")
    return identities


async def create_oauth2_identity(session: AsyncSession, *, request: OAuth2IdentityCreateRequest) -> Identity:
    sql = (
        insert(Identity)
        .values(
            user_id=request,
            iden_type="OAUTH_" + request.provider_id.upper(),
            iden_value=request.provider_uid,
            credential=None,
            status="ACTIVE",
            last_signin_at=None,
            props=request.props or {},
        )
        .returning(Identity)
    )
    logger.debug(f"created oauth identity sql: {sql}")
    identity = await session.exec(sql).one()
    logger.debug(f"created oauth identity: {identity}")
    return identity


async def update_oauth2_identity(
    session: AsyncSession, *, id: uuid.UUID, request: OAuth2IdentityUpdateRequest
) -> Identity | None:
    values = request.model_dump()
    sql = update(Identity).where(Identity.id == id).values(**values, updated_at=utils.utc_now()).returning(Identity)
    logger.debug(f"updated oauth identity sql: {sql}")
    identity = await session.exec(sql).one()
    logger.debug(f"updated oauth identity: {identity}")
    return identity


async def patch_oauth2_identity(
    session: AsyncSession, *, id: uuid.UUID, request: OAuth2IdentityPatchRequest
) -> Identity | None:
    values = request.model_dump(exclude_unset=True)
    if not values:
        logger.info(f"no data to patch, skipped.")
        return None
    sql = update(Identity).where(Identity.id == id).values(**values, updated_at=utils.utc_now()).returning(Identity)
    logger.debug(f"patch oauth identity sql: {sql}")
    identity = await session.exec(sql).one()
    logger.debug(f"patch oauth identity: {identity}")
    return identity


async def delete_identity(session: AsyncSession, *, id: uuid.UUID, soft_delete: bool = False) -> Identity | None:
    if soft_delete:
        sql = (
            update(Identity).where(Identity.id == id).values(status="DELETED", deleted_at=utils.utc_now()).returning(Identity)
        )
    else:
        sql = delete(Identity).where(Identity.id == id).returning(Identity)
    logger.debug(f"delete identity sql: {sql}")

    identity: Identity = await session.exec(sql).first()
    logger.debug(f"deleted identity (soft={soft_delete}): {identity}")
    return identity


async def create_email_identity(session: AsyncSession, *, request: EmailIdentityCreateRequest) -> Identity:
    credential = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    values = request.model_dump(exclude_none=True)
    sql = (
        insert(Identity)
        .values(
            **values,
            credential=credential,
            status="ACTIVE",
            last_signin_at=None,
        )
        .returning(Identity)
    )
    logger.debug(f"created email identity sql: {sql}")
    identity: Identity = await session.exec(sql).one()
    logger.debug(f"created email identity: {identity}")
    return identity


async def update_email_identity(
    session: AsyncSession, *, id: uuid.UUID, request: EmailIdentityUpdateRequest
) -> Identity | None:
    """Update email identity. All fields to update are required, except props."""
    values = request.model_dump()
    if not values:
        logger.info(f"email identity {id} not changed, skipped to update.")
        return None
    sql = update(Identity).where(Identity.id == id).values(**values, updated_at=utils.utc_now()).returning(Identity)
    logger.debug(f"update email identity sql: {sql}")
    identity: Identity = await session.exec(sql).first()
    logger.debug(f"updated email identity: {identity}")
    return identity


async def patch_email_identity(session: AsyncSession, *, id: uuid.UUID, request: EmailIdentityPatchRequest) -> Identity | None:
    """Patch email identity. All fields to patch are optional."""
    values = request.model_dump(exclude_unset=True)
    sql = update(Identity).where(Identity.id == id).values(**values, updated_at=utils.utc_now()).returning(Identity)
    logger.debug(f"patch email identity sql: {sql}")
    identity: Identity = await session.exec(sql).first()
    logger.debug(f"patched email identity: {identity}")
    return identity


async def reset_email_password(session: AsyncSession, *, request: EmailIdentityResetPasswordRequest) -> Identity | None:
    credential = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    sql = (
        update(Identity)
        .where(Identity.iden_type == "EMAIL", Identity.iden_value == request.email)
        .values(credential=credential, updated_at=utils.utc_now())
        .returning(Identity)
    )
    logger.debug(f"reset email password sql: {sql}")
    identity: Identity = await session.exec(sql).first()
    logger.debug(f"upated email identity: {identity}")
    return identity
