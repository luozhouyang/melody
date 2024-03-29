import uuid as uuid_pkg
from datetime import datetime
from enum import Enum

from sqlmodel import Field

from melody.db import BaseModel


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class User(BaseModel, table=True):
    __tablename__ = "user"

    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        title="id",
        description="The unique id of the user",
    )

    username: str = Field(
        default="",
        nullable=False,
        min_length=0,
        max_length=64,
        title="username",
        description="The username of the user",
    )

    nickname: str = Field(
        default="",
        nullable=False,
        min_length=0,
        max_length=64,
        title="nickname",
        description="The nickname of the user",
    )

    email: str = Field(
        default="",
        index=True,
        nullable=False,
        min_length=0,
        max_length=64,
        title="email",
        description="The email of the user",
    )

    phone: str = Field(
        default="",
        nullable=False,
        min_length=0,
        max_length=32,
        title="phone",
        description="The phone number of the user",
    )

    status: UserStatus = Field(
        default=UserStatus.ACTIVE,
        nullable=False,
        title="status",
        description="The status of the user, e.g. active, inactive, deleted",
    )

    last_signin_at: datetime | None = Field(
        default=None,
        nullable=True,
        title="last_signin_at",
        description="Timestamp of last signin",
    )

    def has_beed_deleted(self) -> bool:
        if self.deleted_at is None:
            return False
        if self.deleted_at <= 0:
            return False
        return True
