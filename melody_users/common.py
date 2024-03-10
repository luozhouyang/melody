import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import JSON, TIMESTAMP, UUID, Column, Field, SQLModel


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
