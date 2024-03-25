import uuid
from datetime import datetime
from typing import Literal, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import Index

from ..db import BaseModel

IdentityType = Literal["EMAIL", "PHONE", "OAUTH_GITHUB", "OAUTH_GOOGLE", "OAUTH_FACEBOOK", "OAUTH_WECHAT", "OAUTH_ALIPAY"]
IdentityStatus = Literal["ACTIVE", "INACTIVE", "DELETED"]


class Identity(BaseModel):
    __tablename__ = "identities"
    __table_args__ = (
        Index("ix_identities_iden", "iden_type", "iden_value", unique=True),
        Index("ix_identities_user_id", "user_id", unique=False),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        nullable=False,
        default=uuid.uuid4(),
        primary_key=True,
        comment="The id of the identity",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        index=True,
        nullable=False,
        comment="The user id of this identity",
    )

    iden_type: Mapped[IdentityType] = mapped_column(
        sa.String(16),
        nullable=False,
        comment="Identity type, such as EMAIL, PHONE, OAUTH_GITHUB, OAUTH_GOOGLE",
    )

    iden_value: Mapped[str] = mapped_column(
        sa.String(64),
        nullable=False,
        comment="Identity value, such as email address, phone number, or oauth uid.",
    )

    credential: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=True,
        comment="Credential, such as a bcrypt password.",
    )

    status: Mapped[IdentityStatus] = mapped_column(
        sa.Enum("ACTIVE", "INACTIVE", "DELETED", name="identity_status"),
        nullable=False,
        default="ACTIVE",
        comment="Identity status, such as ACTIVE, INACTIVE, DELETED",
    )

    last_signin_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP,
        nullable=True,
        default=None,
        comment="Timestamp of last signin",
    )
