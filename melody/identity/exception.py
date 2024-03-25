from enum import Enum

from melody.exception import MelodyException


class IdentityError(str, Enum):
    IDENTITY_NOT_FOUND = "error.identity.not_found:Identity not found."
    IDENTITY_ALREADY_EXISTS = "error.identity.already_exists:Identity already exists."


class IdentityException(MelodyException):
    """Identity exception class"""

    @classmethod
    def from_error(cls, error: IdentityError, override_message: str | None = None, **kwargs) -> "IdentityException":
        pair = str(error.value).split(":", 1)
        error_code, error_message = pair[0], pair[1]
        if override_message:
            error_message = override_message
        return cls(code=error_code, message=error_message, **kwargs)
