from typing import Tuple

from sqlmodel import Session

from .model import Auth, User


def user_login_with_github() -> Tuple[Auth, User]:
    pass


def user_logint_with_email(conn: Session, email: str, password: str) -> Tuple[Auth, User]:
    pass
