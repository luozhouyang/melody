import uuid

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class OAuth2IdentityCreateRequest(SQLModel):
    user_id: uuid.UUID = Field(nullable=False, description="The user id of this identity")
    provider_id: str = Field(nullable=False, description="Identity type, such as EMAIL, PHONE, OAUTH_GITHUB, OAUTH_GOOGLE")
    provider_uid: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    props: dict | None = Field(nullable=True, description="Additional properties of the record")


class OAuth2IdentityUpdateRequest(BaseModel):
    user_id: str = Field(nullable=False, description="The user id of this identity")
    provider_id: str = Field(nullable=False, description="Identity type, such as EMAIL, PHONE, OAUTH_GITHUB, OAUTH_GOOGLE")
    provider_uid: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    status: str = Field(nullable=False, description="Identity status, such as ACTIVE, INACTIVE, DELETED")
    props: dict = Field(nullable=False, description="Additional properties of the record")


class OAuth2IdentityPatchRequest(BaseModel):
    user_id: str | None = Field(nullable=True, description="The user id of this identity")
    provider_id: str | None = Field(
        nullable=True, description="Identity type, such as EMAIL, PHONE, OAUTH_GITHUB, OAUTH_GOOGLE"
    )
    provider_uid: str | None = Field(
        nullable=True, description="Identity value, such as email address, phone number, or oauth uid."
    )
    status: str | None = Field(nullable=True, description="Identity status, such as ACTIVE, INACTIVE, DELETED")
    props: dict | None = Field(nullable=True, description="Additional properties of the record")


class EmailIdentityCreateRequest(SQLModel):
    user_id: uuid.UUID = Field(nullable=False, description="The user id of this identity")
    email: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    password: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    props: dict | None = Field(nullable=True, description="Additional properties of the record")


class EmailIdentityUpdateRequest(SQLModel):
    user_id: uuid.UUID = Field(nullable=False, description="The user id of this identity")
    email: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    status: str = Field(nullable=False, description="Identity status, such as ACTIVE, INACTIVE, DELETED")
    props: dict = Field(nullable=False, description="Additional properties of the record")


class EmailIdentityPatchRequest(SQLModel):
    user_id: uuid.UUID | None = Field(nullable=True, description="The user id of this identity")
    email: str | None = Field(nullable=True, description="Identity value, such as email address, phone number, or oauth uid.")
    status: str | None = Field(nullable=True, description="Identity status, such as ACTIVE, INACTIVE, DELETED")


class EmailIdentityResetPasswordRequest(SQLModel):
    email: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
    password: str = Field(nullable=False, description="Identity value, such as email address, phone number, or oauth uid.")
