import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from melody import utils

from .models import OAuth2IdentityCreateRequest, OAuth2IdentityPatchRequest, OAuth2IdentityUpdateRequest
from .tables import Identity


async def create_oauth2_identity(session: AsyncSession, request: OAuth2IdentityCreateRequest) -> Identity:
    iden = Identity(
        user_id=request.user_id,
        iden_type=request.provider_id,
        iden_value=request.provider_uid,
        credential=None,
        status="ACTIVE",
        last_signin_at=None,
        props={"provider_props": request.provider_props} if request.provider_props else {},
    )
    session.add(iden)
    await session.commit()
    await session.refresh(iden)
    return iden


async def update_oauth2_identity(
    id: uuid.UUID, session: AsyncSession, request: OAuth2IdentityUpdateRequest
) -> Identity | None:
    iden = await session.get(Identity, id)
    if not iden:
        return None
    if request.user_id:
        iden.user_id = request.user_id
    if request.status:
        iden.status = request.status
    if request.provider_id:
        iden.iden_type = request.provider_id
    if request.provider_uid:
        iden.iden_value = request.provider_uid
    if request.props:
        iden.props = request.props
    iden.updated_at = utils.utc_now()
    session.add(iden)
    await session.commit()
    await session.refresh(iden)
    return iden


async def patch_oauth2_identity(id: uuid.UUID, session: AsyncSession, request: OAuth2IdentityPatchRequest) -> Identity | None:
    iden = await session.get(Identity, id)
    if not iden:
        return None
    if request.user_id:
        iden.user_id = request.user_id
    if request.status:
        iden.status = request.status
    if request.provider_id:
        iden.iden_type = request.provider_id
    if request.provider_uid:
        iden.iden_value = request.provider_uid
    if request.props:
        props = iden.props or {}
        props.update(request.props)
    iden.updated_at = utils.utc_now()
    session.add(iden)
    await session.commit()
    await session.refresh(iden)
    return iden


async def delete_oauth2_identity(id: uuid.UUID, session: AsyncSession) -> Identity | None:
    iden = await session.get(Identity, id)
    if not iden:
        return None
    iden.deleted_at = utils.utc_now()
    iden.status = "DELETED"
    session.add(iden)
    await session.commit()
    await session.refresh(iden)
    return iden
