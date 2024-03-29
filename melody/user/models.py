from sqlmodel import SQLModel


class UserCreateRequest(SQLModel):
    """Create user"""

    username: str | None = ""
    nickname: str | None = ""
    email: str | None = ""
    phone: str | None = ""
    props: dict | None = None


class UserUpdateRequest(SQLModel):
    """Update user, override all fields."""

    username: str
    nickname: str
    email: str
    phone: str
    props: dict


class UserPatchRequest(SQLModel):
    """Patch user, override non-null fields only."""

    username: str | None = None
    nickname: str | None = None
    email: str | None = None
    phone: str | None = None
    props: dict | None = None
