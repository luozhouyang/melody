from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    tenant_id: Optional[str] = Field(
        default="",
        index=True,
        description="tenant id",
        max_length=32,
        min_length=32,
        sa_column_kwargs={"server_default": text("''")},
    )
    created_at: Optional[datetime] = Field(
        nullable=False,
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP()"),
            # "oncreate": text("CURRENT_TIMESTAMP()"),
        },
    )
    updated_at: Optional[datetime] = Field(
        nullable=False,
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP()"),
            "onupdate": text("CURRENT_TIMESTAMP()"),
        },
    )
    deleted_at: Optional[datetime] = Field(
        default=0,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("0"),
        },
    )
    is_deleted: Optional[int] = Field(
        default=0,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("0"),
        },
    )
    props: Optional[str] = Field(
        default=None,
        nullable=True,
        sa_column_kwargs={
            "server_default": text("NULL"),
        },
    )


class AuthType(Enum):
    EMAIL = "EMAIL"
    GITHUB = "GITHUB"
    WECHAT = "WECHAT"
    ALIPAY = "ALIPAY"


class CredType(Enum):
    PASSWORD = "PASSWORD"
    OAUTH = "OAUTH"


class Auth(BaseModel, table=True):
    id: Optional[int] = Field(default=None, nullable=False, unique=True, primary_key=True)
    user_id: str = Field(nullable=False, index=True, max_length=32, min_length=32)
    auth_type: AuthType = Field(nullable=False)
    auth_value: str
    cred_type: CredType = Field(nullable=False)
    cred_value: str = Field(default="")


class User(BaseModel, table=True):
    id: Optional[int] = Field(default=None, nullable=False, unique=True, primary_key=True)
    avatar: Optional[str] = Field(default="")
    username: str = Field(default="")
    nickname: str = Field(default="")
    email: str = Field(default="")
