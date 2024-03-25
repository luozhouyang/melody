import uuid

from fastapi import APIRouter

from melody import deps

from . import crud, models, tables

router = APIRouter()


@router.post("/identities/oauth2")
async def create_oauth2_identity(
    session: deps.DatabaseSession, request: models.OAuth2IdentityCreateRequest
) -> tables.Identity:
    return await crud.create_oauth2_identity(session, request)


@router.post("/identities/oauth2/{id}")
async def update_oauth2_identity(
    id: uuid.UUID, session: deps.DatabaseSession, request: models.OAuth2IdentityUpdateRequest
) -> tables.Identity | None:
    return await crud.update_oauth2_identity(id, session, request)


@router.patch("/identities/oauth2/{id}")
async def patch_oauth2_identity(
    id: uuid.UUID, session: deps.DatabaseSession, request: models.OAuth2IdentityPatchRequest
) -> tables.Identity | None:
    return await crud.patch_oauth2_identity(id, session, request)


@router.delete("/identities/oauth2/{id}")
async def delete_oauth2_identity(id: uuid.UUID, session: deps.DatabaseSession) -> tables.Identity | None:
    return await crud.delete_oauth2_identity(id, session)
