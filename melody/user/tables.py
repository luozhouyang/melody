import uuid
from datetime import datetime

from sqlmodel import Field

from melody.db import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default=uuid.uuid4(),
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

    status: str = Field(
        default="ACTIVE",
        nullable=False,
        title="status",
        description="The status of the user, enum: ACTIVE, INACTIVE, DELETED",
    )

    last_signin_at: datetime | None = Field(
        default=None,
        nullable=True,
        title="last_signin_at",
        description="Timestamp of last signin",
    )
