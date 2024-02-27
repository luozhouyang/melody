import logging
from datetime import datetime
from typing import Optional, Tuple, Union

from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import oauth2_settings
from .tables import Identity, OAuth2State, Session, User

logger = logging.getLogger(__name__)


async def _login_with_oauth(engine: AsyncEngine, provider_id: str, **kwargs) -> str:
    """Login with oauth"""
    registered_client = oauth2_settings.get_client(provider_id=provider_id)
    if not registered_client:
        raise ValueError(f"Cannot find registered client for provider {provider_id}")

    oauth_provider = oauth2_settings.get_provider(provider_id=provider_id)
    if not oauth_provider:
        raise ValueError(f"Cannot find provider {provider_id}")

    scope = None
    if isinstance(registered_client.scope, str):
        scope = registered_client.scope
    elif isinstance(registered_client.scope, list):
        scope = " ".join(registered_client.scope)
    oauth_client = AsyncOAuth2Client(
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        scope=scope,
        redirect_uri=registered_client.redirect_uri,
        code_challenge_method=registered_client.code_challenge_method,
    )
    url, state = oauth_client.create_authorization_url(
        url=oauth_provider.auth_url,
        code_verifier=registered_client.client_secret,
    )

    async with AsyncSession(engine) as session:
        # save oauth2 state
        oauth_state = OAuth2State(
            state=state,
            provider=provider_id,
            client_id=registered_client.client_id,
            code_challenge=registered_client.client_secret,
            code_challenge_method=registered_client.code_challenge_method,
            tenant_id=kwargs.get("tenant_id", None),
        )
        session.add(oauth_state)
        session.commit()
        logger.debug(f"Saving oauth2 state: {oauth_state}")
    return url


async def _resolve_oauth_state(session: AsyncSession, state: str, **kwargs) -> OAuth2State:
    statment = select(OAuth2State).where(OAuth2State.state == state)
    oauth_state = await session.exec(statment).one_or_none()
    if not oauth_state:
        raise ValueError(f"Cannot find oauth2 state for state {state}")
    expires_at = oauth_state.expires_at
    if expires_at is not None and 0 < expires_at < datetime.utcnow():
        session.delete(oauth_state)
        session.commit()
        logger.warning(f"OAuth2 state expired")
        raise ValueError(f"OAuth2 state expired")
    return oauth_state


async def _resolve_oauth_token(oauth_state: OAuth2State, code: str, **kwargs) -> dict:
    registered_client = oauth2_settings.get_client(provider_id=oauth_state.provider)
    if not registered_client:
        raise ValueError(f"Cannot find registered client for provider {oauth_state.provider}")
    if registered_client.client_id != oauth_state.client_id:
        raise ValueError(f"Invalid oauth2 state, client id mismatch")

    oauth_client = AsyncOAuth2Client(
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        scope=registered_client.code_challenge_method,
        redirect_uri=registered_client.redirect_uri,
    )
    oauth_provider = oauth2_settings.get_provider(provider_id=oauth_state.provider)
    if not oauth_provider:
        raise ValueError(f"Cannot find provider {oauth_state.provider}")
    token = await oauth_client.fetch_token(
        url=oauth_provider.token_url,
        grant_type="authorization_code",
        code=code,
        redirect_uri=registered_client.redirect_uri,
    )
    return token


async def _login_with_oauth_callback(engine: AsyncEngine, code: str, state: str, **kwargs):
    async with AsyncSession(engine) as session:
        oauth_state = await _resolve_oauth_state(session=session, state=state, **kwargs)
        oauth_token = await _resolve_oauth_token(oauth_state=oauth_state, code=code, **kwargs)
        # save access token

        # create user

        # create identity

        # delete state


class UserService:
    """The User Service"""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def login_with_oauth(self, provider_id: str, **kwargs) -> str:
        """Login with oauth.

        Parameters:
        -----------
        provider_id: str, the id of the oauth provider, such as 'github', 'google', 'facebook', etc.

        Returns:
        --------
        url: str, the authorization url

        Raises:
        -------
        ValueError: If the provider is not supported, or no registered client for the provider.

        Examples:
        ---------
        >>> from melody_users.service import UserService
        >>> from melody_users.tables import User
        >>> from sqlalchemy.ext.asyncio import create_async_engine
        >>> engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        >>> user_service = UserService(engine)
        >>> url = await user_service.login_with_oauth('github')
        >>> print(url)
        """
        authorization_url = await _login_with_oauth(self._engine, provider_id, **kwargs)
        logger.debug(f"Login with oauth: {authorization_url}")
        return authorization_url

    async def login_with_oauth_callback(self, code: str, state: str, **kwargs) -> Union[str, None]:
        """Login with oauth callback"""
        raise NotImplementedError

    async def login_with_password(self, email: str, password: str, **kwargs) -> Union[str, None]:
        """Login with password"""
        raise NotImplementedError
