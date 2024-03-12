import os
import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata = MetaData(schema=os.environ.get("DB_SCHEMA", "public"))


class Base(DeclarativeBase):
    metadata = metadata

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.UUID,
        nullable=True,
        default=None,
        comment="The tenant id of the record",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP,
        nullable=False,
        default_factory=datetime.utcnow,
        comment="Timestamp of record creation",
    )

    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP,
        nullable=False,
        default_factory=datetime.utcnow,
        comment="Timestamp of record update",
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP,
        nullable=True,
        default=None,
        comment="Timestamp of record deletion",
    )

    props: Mapped[Optional[dict]] = mapped_column(
        sa.JSON,
        nullable=True,
        default=None,
        comment="Additional properties of the record",
    )
