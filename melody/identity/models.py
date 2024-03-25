import uuid

from sqlmodel import Field, SQLModel


class EmailPasswordIdentityCreateRequest(SQLModel):
    """Create identity by email and password."""

    user_id: uuid.UUID
    email: str
    password: str
    props: dict | None = None


class OAuth2IdentityCreateRequest(SQLModel):
    """Create identity by OAuth2"""

    user_id: uuid.UUID
    provider_id: str
    provider_uid: str
    provider_props: dict | None = None


class OAuth2IdentityUpdateRequest(SQLModel):
    """Update identity by OAuth2"""

    user_id: uuid.UUID | None = None
    status: str | None = None
    provider_id: str | None = None
    provider_uid: str | None = None
    props: dict | None = None


class OAuth2IdentityPatchRequest(SQLModel):
    """Patch identity by OAuth2"""

    user_id: uuid.UUID | None = None
    status: str | None = None
    provider_id: str | None = None
    provider_uid: str | None = None
    props: dict | None = None
