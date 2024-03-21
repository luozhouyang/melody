import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel, table=False):

    tenant_id: str | None = Field(
        nullable=True,
        default=None,
        comment="The tenant id of the record",
        sa_column=sa.Column(sa.String(64), default=None),
    )

    created_at: datetime = Field(
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="Timestamp of record creation",
        sa_column=sa.Column(sa.TIMESTAMP, default=datetime.now(timezone.utc)),
    )

    updated_at: datetime = Field(
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="Timestamp of record update",
        sa_column=sa.Column(sa.TIMESTAMP, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)),
    )

    deleted_at: datetime | None = Field(
        nullable=True,
        default=None,
        comment="Timestamp of record deletion",
        sa_column=sa.Column(sa.TIMESTAMP, default=None),
    )

    props: dict | None = Field(
        nullable=True,
        default=None,
        comment="Additional properties of the record",
        sa_column=sa.Column(sa.JSON, default={}),
    )
