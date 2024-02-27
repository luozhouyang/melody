import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, TIMESTAMP, UUID, Column, String
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model for all tables"""

    tenant_id: Optional[uuid.UUID] = Field(
        default="",
        index=True,
        sa_column=Column(UUID, default=uuid.uuid4),
        description="The tenant id of the record",
    )

    created_at: Optional[datetime] = Field(
        nullable=False,
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of record creation",
    )

    updated_at: Optional[datetime] = Field(
        nullable=False,
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of record update",
    )

    deleted_at: Optional[datetime] = Field(
        default=0,
        nullable=False,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of record deletion",
    )

    props: dict = Field(
        default=None,
        nullable=True,
        sa_column=Column(JSON, default=None),
        description="Additional properties of the record",
    )


class User(BaseModel, table=True):
    __tablename__ = "users"

    username: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(64), default=""),
        description="The username of the user",
    )

    nickname: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(64), default=""),
        description="The nickname of the user",
    )

    email: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(64), default=""),
        description="The email of the user",
    )

    phone: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(64), default=""),
        description="The phone of the user",
    )

    status: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(32), default=""),
        description="The status of the user, e.g. active, inactive, deleted",
    )


class Identity(BaseModel, table=True):
    __tablename__ = "identities"

    user_id: uuid.UUID = Field(
        default=uuid.uuid4,
        nullable=False,
        sa_column=Column(UUID, default=uuid.uuid4),
        description="The user id of the record",
    )

    auth_type: str = Field(
        default="",
        nullable=False,
        sa_column=Column(String(32), default=""),
        description="The auth type of the record",
    )

    auth_value: str = Field(
        default="",
        nullable=False,
        sa_column=Column(String(256), default=""),
        description="The auth value of the record",
    )

    status: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(32), default=""),
        description="The status of the record, e.g. active, inactive, deleted",
    )

    last_signin_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of last signin",
    )


class Session(BaseModel, table=True):
    __tablename__ = "sessions"

    user_id: uuid.UUID = Field(
        nullable=False,
        sa_column=Column(UUID, default=uuid.uuid4),
        description="The user id of the session",
    )

    iden_id: uuid.UUID = Field(
        nullable=False,
        sa_column=Column(UUID, default=uuid.uuid4),
        description="The identity id of the session",
    )

    auth_token: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(256), default=""),
        description="The auth token of the session",
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of session expiration",
    )

    refreshed_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of session refresh",
    )

    user_agent: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(256), default=""),
        description="The user agent of the session",
    )

    ip_address: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String(256), default=""),
        description="The ip address of the session",
    )


class OAuth2State(BaseModel, table=True):
    __tablename__ = "oauth2_states"

    state: str = Field(
        nullable=False,
        sa_column=Column(String, default=""),
        description="The state of the oauth2 state",
    )

    provider: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String, default=""),
        description="The provider of the oauth2 state",
    )

    client_id: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String, default=""),
        description="The client id of the oauth2 state",
    )

    code_challenge: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String, default=""),
        description="The code challenge of the oauth2 state",
    )

    code_challenge_method: Optional[str] = Field(
        default="",
        nullable=False,
        sa_column=Column(String, default=""),
        description="The code challenge method of the oauth2 state",
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_column=Column(TIMESTAMP),
        description="Timestamp of oauth2 state expiration",
    )
