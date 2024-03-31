import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):

    class Config:
        orm_mode = True

    tenant_id: str = Field(
        default="",
        nullable=False,
        title="tenant_id",
        description="The tenant id of the record",
        min_length=0,
        max_length=64,
    )

    created_at: datetime = Field(
        nullable=False,
        default=datetime.now(timezone.utc),
        title="created_at",
        description="Timestamp of record creation",
    )

    updated_at: datetime = Field(
        nullable=False,
        default=datetime.now(timezone.utc),
        title="updated_at",
        description="Timestamp of record update",
    )

    deleted_at: datetime | None = Field(
        nullable=True,
        default=None,
        title="deleted_at",
        description="Timestamp of record deletion",
    )

    props: dict = Field(
        nullable=False,
        default={},
        title="props",
        description="Additional properties of the record",
        sa_type=sa.JSON,
    )

    def is_deleted(self) -> bool:
        if self.deleted_at is None:
            return False
        if self.deleted_at <= 0:
            return False
        return True
