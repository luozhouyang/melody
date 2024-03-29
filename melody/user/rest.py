import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlmodel import select, update

from . import crud
from .models import UserCreateRequest, UserPatchRequest, UserUpdateRequest
from .tables import User

router = APIRouter()


@router.post("/users")
async def create_user(request: UserCreateRequest) -> User:
    return await crud.create_user(request)


@router.post("/users/{id}")
async def update_user(id: uuid.UUID, request: UserUpdateRequest) -> User | None:
    return await crud.update_user(id, request)


@router.patch("/users/{id}")
async def patch_user(id: uuid.UUID, request: UserPatchRequest) -> User | None:
    return await crud.patch_user(id, request)


@router.delete("/users/{id}")
async def delete_user(id: uuid.UUID) -> User | None:
    return await crud.delete_user(id)
