import uuid

from fastapi import APIRouter

from melody import deps

from . import crud, models, tables

router = APIRouter()


@router.post("/identities/oauth2")
async def create_oauth2_identity(
    session: deps.DatabaseSession, request: models.OAuth2IdentityCreateRequest
) -> tables.Identity:
    return await crud.create_oauth2_identity(session, request=request)


@router.post("/identities/oauth2/{id}")
async def update_oauth2_identity(
    session: deps.DatabaseSession, id: uuid.UUID, request: models.OAuth2IdentityUpdateRequest
) -> tables.Identity | None:
    return await crud.update_oauth2_identity(session, id=id, request=request)


@router.patch("/identities/oauth2/{id}")
async def patch_oauth2_identity(
    session: deps.DatabaseSession, id: uuid.UUID, request: models.OAuth2IdentityPatchRequest
) -> tables.Identity | None:
    return await crud.patch_oauth2_identity(session, id=id, request=request)


@router.delete("/identities/oauth2/{id}")
async def delete_oauth2_identity(session: deps.DatabaseSession, id: uuid.UUID) -> tables.Identity | None:
    return await crud.delete_oauth2_identity(session, id=id)


@router.post("/identities/email")
async def create_email_identity(session: deps.DatabaseSession, request: models.EmailIdentityCreateRequest) -> tables.Identity:
    return await crud.create_email_identity(session, request=request)


@router.post("/identities/email/{id}")
async def update_email_identity(
    session: deps.DatabaseSession, id: uuid.UUID, request: models.EmailIdentityUpdateRequest
) -> tables.Identity | None:
    return await crud.update_email_identity(session, id=id, request=request)


@router.patch("/identities/email/{id}")
async def patch_email_identity(
    session: deps.DatabaseSession, id: uuid.UUID, request: models.EmailIdentityPatchRequest
) -> tables.Identity | None:
    return await crud.patch_email_identity(session, id=id, request=request)


@router.delete("/identities/email/{id}")
async def delete_email_identity(session: deps.DatabaseSession, id: uuid.UUID) -> tables.Identity | None:
    return await crud.delete_identity(session, id=id)


@router.post("/identities/email/resetpw")
async def reset_email_password(
    session: deps.DatabaseSession, request: models.EmailIdentityResetPasswordRequest
) -> tables.Identity | None:
    return await crud.reset_email_password(session, request=request)
