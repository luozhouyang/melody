import uuid

from fastapi import APIRouter

from melody import deps

from . import crud
from .models import UserCreateRequest, UserPatchRequest, UserUpdateRequest
from .tables import User

router = APIRouter()


@router.post("/users")
async def create_user(session: deps.DatabaseSession, request: UserCreateRequest) -> User:
    return await crud.create_user(session, request=request)


@router.post("/users/{id}")
async def update_user(session: deps.DatabaseSession, id: uuid.UUID, request: UserUpdateRequest) -> User | None:
    return await crud.update_user(session, id=id, request=request)


@router.patch("/users/{id}")
async def patch_user(session: deps.DatabaseSession, id: uuid.UUID, request: UserPatchRequest) -> User | None:
    return await crud.patch_user(session, id=id, request=request)


@router.delete("/users/{id}")
async def delete_user(session: deps.DatabaseSession, id: uuid.UUID) -> User | None:
    return await crud.delete_user(session, id=id, soft_delete=True)
