import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from ..db_base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        primary_key=True,
        default=uuid.uuid4,
        comment="The unique id of the user",
    )

    username: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        default="",
        comment="The username of the user",
    )

    nickname: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        default="",
        comment="The nickname of the user",
    )

    email: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        default="",
        comment="The email of the user",
    )

    phone: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        default="",
        comment="The phone of the user",
    )

    status: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        default="",
        comment="The status of the user, e.g. active, inactive, deleted",
    )

    last_signin_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP,
        nullable=True,
        default=None,
        comment="Timestamp of last signin",
    )

    def has_beed_deleted(self) -> bool:
        if self.deleted_at is None:
            return False
        if self.deleted_at <= 0:
            return False
        return True
