import logging
import uuid
from typing import List

import bcrypt
from sqlalchemy import delete, insert, select, update

from melody import utils
from melody.deps import database

from .tables import Identity

logger = logging.getLogger("melody.identity")


async def retrieve_identity(id: uuid.UUID) -> Identity | None:
    sql = select(Identity).where(Identity.id == id)
    logger.debug(f"retrieving identity sql: {sql}")
    identity = await database.execute(sql)
    logger.debug(f"retrieved identity: {identity}")
    return identity


async def retrieve_identities_by_user_id(user_id: uuid.UUID) -> List[Identity] | None:
    sql = select(Identity).where(Identity.user_id == user_id)
    logger.debug(f"retrieving identity sql: {sql}")
    identity = await database.fetch_all(sql)
    logger.debug(f"retrieved identity: {identity}")
    return identity


@database.transaction()
async def create_oauth2_identity(
    user_id: uuid.UUID, provider_id: str, provider_uid: str, props: dict | None = None
) -> Identity:
    sql = (
        insert(Identity)
        .values(
            user_id=user_id,
            iden_type="OAUTH_" + provider_id.upper(),
            iden_value=provider_uid,
            credential=None,
            status="ACTIVE",
            last_signin_at=None,
            props=props or {},
        )
        .returning(Identity)
    )
    logger.debug(f"created oauth identity sql: {sql}")
    identity = await database.execute(sql)
    logger.debug(f"created oauth identity: {identity}")
    return identity


@database.transaction()
async def update_oauth2_identity(
    id: uuid.UUID, user_id: uuid.UUID, provider_id: str, provider_uid: str, status: str, props: dict
) -> Identity | None:
    sql = (
        update(Identity)
        .where(Identity.id == id)
        .values(
            user_id=user_id,
            iden_type="OAUTH_" + provider_id.upper(),
            iden_value=provider_uid,
            status=status,
            props=props,
            updated_at=utils.utc_now(),
        )
        .returning(Identity)
    )
    logger.debug(f"updated oauth identity sql: {sql}")
    identity = database.execute(sql)
    logger.debug(f"updated oauth identity: {identity}")
    return identity


@database.transaction()
async def patch_oauth2_identity(
    id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    provider_id: str | None = None,
    provider_uid: str | None = None,
    status: str | None = None,
    props: dict | None = None,
) -> Identity | None:
    data = {}
    if user_id:
        data["user_id"] = user_id
    if provider_id:
        data["iden_type"] = "OAUTH_" + provider_id.upper()
    if provider_uid:
        data["iden_value"] = provider_uid
    if status:
        data["status"] = status
    if props:
        data["props"] = props
    if not data:
        logger.info(f"no data to patch, skipped.")
        return None
    sql = update(Identity).where(Identity.id == id).values(**data, updated_at=utils.utc_now()).returning(Identity)
    logger.debug(f"patch oauth identity sql: {sql}")
    identity = database.execute(sql)
    logger.debug(f"patch oauth identity: {identity}")
    return identity


@database.transaction()
async def delete_identity(id: uuid.UUID, soft_delete: bool = False) -> Identity | None:
    if soft_delete:
        sql = (
            update(Identity).where(Identity.id == id).values(status="DELETED", deleted_at=utils.utc_now()).returning(Identity)
        )
    else:
        sql = delete(Identity).where(Identity.id == id).returning(Identity)
    logger.debug(f"delete identity sql: {sql}")

    identity: Identity = database.execute(delete(Identity).where(Identity.id == id).returning(Identity))
    if identity:
        identity.credential = None
    logger.debug(f"deleted identity (soft={soft_delete}): {identity}")
    return identity


@database.transaction()
async def create_email_identity(user_id: uuid.UUID, email: str, password: str, props: dict | None = None) -> Identity:
    credential = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    sql = (
        insert(Identity)
        .values(
            user_id=user_id,
            iden_type="EMAIL",
            iden_value=email,
            credential=credential,
            status="ACTIVE",
            last_signin_at=None,
            props=props or {},
        )
        .returning(Identity)
    )
    logger.debug(f"created email identity sql: {sql}")
    identity: Identity = await database.execute(sql)
    logger.debug(f"created email identity: {identity}")
    return identity


@database.transaction()
async def update_email_identity(
    id: uuid.UUID, user_id: uuid.UUID, email: str, status: str, props: dict | None = None
) -> Identity | None:
    """Update email identity. All fields to update are required, except props."""
    data = {
        "user_id": user_id,
        "iden_type": "EMAIL",
        "iden_value": email,
        "status": status,
        "updated_at": utils.utc_now(),
    }
    if props:
        data["props"] = props
    if not data:
        logger.info(f"email identity {id} not changed, skipped to update.")
        return None
    sql = update(Identity).where(Identity.id == id).values(**data).returning(Identity)
    logger.debug(f"update email identity sql: {sql}")
    identity: Identity = await database.execute(sql)
    logger.debug(f"updated email identity: {identity}")
    return identity


@database.transaction()
async def reset_email_password(email: str, password: str) -> Identity | None:
    credential = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    sql = (
        update(Identity)
        .where(Identity.iden_type == "EMAIL", Identity.iden_value == email)
        .values(credential=credential, updated_at=utils.utc_now())
        .returning(Identity)
    )
    logger.debug(f"reset email password sql: {sql}")
    identity: Identity = database.execute(sql)
    logger.debug(f"upated email identity: {identity}")
    return identity
