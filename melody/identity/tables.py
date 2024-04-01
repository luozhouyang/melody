import uuid
from datetime import datetime

from pydantic import SecretStr
from sqlmodel import Field, Index

from melody.db import BaseModel


class Identity(BaseModel):
    __tablename__ = "identities"
    __table_args__ = (
        Index("ix_identities_iden", "iden_type", "iden_value", unique=True),
        Index("ix_identities_user_id", "user_id", unique=False),
    )

    id: uuid.UUID = Field(
        default=uuid.uuid4(),
        nullable=False,
        primary_key=True,
        description="The id of the identity",
    )

    user_id: uuid.UUID = Field(
        index=True,
        nullable=False,
        description="The user id of this identity",
    )

    iden_type: str = Field(
        nullable=False,
        description="Identity type, such as EMAIL, PHONE, OAUTH_GITHUB, OAUTH_GOOGLE",
    )

    iden_value: str = Field(
        nullable=False,
        description="Identity value, such as email address, phone number, or oauth uid.",
    )

    credential: SecretStr | None = Field(
        default=None,
        nullable=True,
        description="Credential, such as a bcrypt password.",
    )

    status: str = Field(
        default="ACTIVE",
        nullable=False,
        description="Identity status, such as ACTIVE, INACTIVE, DELETED",
    )

    last_signin_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp of last signin",
    )
