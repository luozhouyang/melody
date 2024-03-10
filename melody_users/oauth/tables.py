from typing import Optional

from sqlmodel import VARCHAR, Column, Field

from ..common import BaseModel


class OAuth2Client(BaseModel):
    """Registered OAuth Client"""

    __tablename__ = "oauth_clients"

    provider: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth provider name",
    )

    client_id: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth client id",
    )

    client_secret: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth client secret",
    )

    scope: Optional[str] = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth client scope",
    )

    redirect_uri: Optional[str] = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth client redirect url",
    )

    code_challenge_method: Optional[str] = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth client code challenge method",
    )


class OAuth2Provider(BaseModel):
    """OAuth2 Provider"""

    __tablename__ = "oauth_providers"

    name: str = Field(
        nullable=False,
        index=True,
        unique=True,
        sa_column=Column(VARCHAR(255), nullable=False, unique=True, index=True),
        description="OAuth provider name",
    )

    auth_url: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth authorization url",
    )

    token_url: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth token url",
    )

    user_url: str = Field(
        nullable=False,
        sa_column=Column(VARCHAR(255), nullable=False),
        description="OAuth userinfo url",
    )
