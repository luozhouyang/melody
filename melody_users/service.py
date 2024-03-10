import logging
import uuid
from datetime import datetime, timedelta
from authlib.common.security import generate_token
from typing import Optional, Tuple, Union
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .oauth import AbstractOAuth2ClientService, AbstractOAuth2ProviderService, OAuth2Client, OAuth2Provider
from .oauth.service import DatabaseOAuth2ClientService, DatabaseOAuth2ProviderService
from .settings import oauth2_settings
from .tables import Identity, OAuth2State, OAuth2Token, Session, User

logger = logging.getLogger(__name__)


class UserService:
    """The User Service"""

    def __init__(self, engine: AsyncEngine, tenant_id: uuid.UUID, **kwargs) -> None:
        self._engine = engine
        self._tenant_id = tenant_id
        self._oauth2_provider_service = DatabaseOAuth2ProviderService(engine=engine)
        self._oauth2_client_service = DatabaseOAuth2ClientService(engine=engine, tenant_id=tenant_id)

    async def login_with_oauth(self, provider: str, client_id: str, **kwargs) -> str:
        """Login with oauth.

        Parameters:
        -----------
        provider: str, the name of the oauth provider, such as 'github', 'google', 'facebook', etc.
        client_id: str, the client id of the oauth client

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
        >>> user_service = UserService(engine, tenant_id="Your tenant id")
        >>> url = await user_service.login_with_oauth('github')
        >>> print(url)
        """
        oauth2_client = await self._oauth2_client_service.get_client(provider=provider, client_id=client_id)
        if not oauth2_client:
            raise ValueError(f"Cannot find registered client for provider {provider}")

        oauth2_provider = await self._oauth2_provider_service.get_provider(provider=provider)
        if not oauth2_provider:
            raise ValueError(f"Cannot find provider {provider}")

        def _resolve_code_challenge_method():
            if not oauth2_client.code_challenge_method:
                return None
            return oauth2_client.code_challenge_method

        scope = self._resolve_oauth2_scope(oauth2_client)
        code_challenge_method = _resolve_code_challenge_method()
        code_verifier = generate_token(length=64)
        oauth_client = AsyncOAuth2Client(
            client_id=oauth2_client.client_id,
            client_secret=oauth2_client.client_secret,
            redirect_uri=oauth2_client.redirect_uri,
            scope=scope,
        )
        url, state = oauth_client.create_authorization_url(
            url=oauth2_provider.auth_url,
            response_type="code",
            code_verifier=code_verifier,
            code_challenge_method=code_challenge_method,
        )

        async with AsyncSession(self._engine) as session:
            # save oauth2 state
            oauth_state = OAuth2State(
                state=state,
                provider=provider,
                client_id=oauth2_client.client_id,
                code_verifier=code_verifier,
                code_challenge_method=code_challenge_method,
                expires_at=datetime.utcnow() + timedelta(days=0, seconds=60),
                tenant_id=self._tenant_id,
            )
            session.add(oauth_state)
            await session.commit()
            await session.refresh(oauth_state)
            logger.debug(f"saved oauth2 state: {oauth_state}")
        logger.debug(f"Login with oauth: {url}")
        return url

    async def login_with_oauth_callback(self, code: str, state: str, **kwargs) -> Union[str, None]:
        """Login with oauth callback"""
        async with AsyncSession(self._engine) as session:
            oauth2_state = await self._resolve_oauth2_state(session=session, state=state, **kwargs)
            session.delete(oauth2_state)

            oauth2_client = await self._resolve_oauth2_client(oauth2_state=oauth2_state, **kwargs)
            oauth2_provider = await self._resolve_oauth2_provider(oauth2_state=oauth2_state, **kwargs)
            # fetch token response
            token = await self._exchange_oauth2_token(
                oauth2_client=oauth2_client,
                oauth2_provider=oauth2_provider,
                oauth2_state=oauth2_state,
                code=code,
            )
            logger.debug(f"fetched token from provider: {token}")
            # fetch user info
            user = await self._fetch_user_info(url=oauth2_provider.user_url, access_token=token.get("access_tokeen"))
            logger.debug(f"fetched user info: {user}")
            # create user

            # create identity

            # save oauth2 tokens
            oauth2_token = OAuth2Token(
                provider=oauth2_client.provider,
                client_id=oauth2_client.client_id,
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=datetime.utcnow() + timedelta(days=0, seconds=token.get("expires_at", 0)),
                scope=token.get("scope"),
                tenant_id=self._tenant_id,
            )
            session.add(oauth2_token)
            session.refresh()
            # delete state

    async def login_with_password(self, email: str, password: str, **kwargs) -> Union[str, None]:
        """Login with password"""
        raise NotImplementedError

    async def _upsert_user(self, session: AsyncSession, user: dict, **kwargs) -> User:
        user = User(**user)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def _fetch_user_info(self, url: str, access_token: str, **kwargs):
        async with httpx.get(
            url=url,
            headers={"Authorization": f"Bearer {access_token}"},
        ) as response:
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Cannot fetch user info: {response.text}")

    async def _save_access_token(self, session: AsyncSession, oauth_client, oauth2_token: dict, **kwargs) -> OAuth2Token:
        statement = select(OAuth2Token).where(OAuth2Token.provider == oauth_client.provider)
        now = datetime.now()
        expires_at = now + timedelta(days=0, seconds=oauth2_token.get("expires_at", 0))
        token = OAuth2Token(
            provider=oauth_client.provider,
            client_id=oauth_client.client_id,
            access_token=oauth2_token.get("access_token"),
            refresh_token=oauth2_token.get("refresh_token"),
            expires_at=expires_at,
            scope=oauth2_token.get("scope", ""),
            tenant_id=self._tenant_id,
        )
        session.add(token)

    async def _exchange_oauth2_token(
        self, oauth2_client: OAuth2Client, oauth2_provider: OAuth2Provider, oauth2_state: OAuth2State, code: str
    ) -> dict:
        client = AsyncOAuth2Client(
            client_id=oauth2_client.client_id,
            client_secret=oauth2_client.client_secret,
            scope=self._resolve_oauth2_scope(oauth2_client),
            redirect_uri=oauth2_client.redirect_uri,
            code_challenge_method=oauth2_client.code_challenge_method,
        )
        token = await client.fetch_token(
            url=oauth2_provider.token_url,
            grant_type="authorization_code",
            code=code,
            code_verifier=oauth2_state.code_verifier,
        )
        return token

    async def _resolve_oauth2_state(self, session: AsyncSession, state: str, **kwargs) -> OAuth2State:
        statment = select(OAuth2State).where(OAuth2State.state == state, OAuth2State.tenant_id == self._tenant_id)
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

    async def _resolve_oauth2_client(self, oauth2_state: OAuth2State, **kwargs):
        provider = oauth2_state.provider
        client_id = oauth2_state.client_id
        oauth2_client = await self._oauth2_client_service.get_client(provider=provider, client_id=client_id)
        if not oauth2_client:
            raise ValueError(f"Cannot find registered client for provider {provider}")
        if oauth2_client.client_id != client_id:
            raise ValueError(f"Invalid oauth2 state, client id mismatch")
        return oauth2_client

    async def _resolve_oauth2_provider(self, oauth2_state: OAuth2State, **kwargs) -> OAuth2Provider:
        oauth2_provider = self._oauth2_provider_service.get_provider(provider=oauth2_state.provider)
        if not oauth2_provider:
            raise ValueError(f"Cannot find provider {oauth2_state.provider}")
        return oauth2_provider

    async def _resolve_oauth2_scope(self, oauth2_client: OAuth2Client, **kwargs):
        if not oauth2_client.scope:
            return None
        scopes = str(oauth2_client.scope).split()
        return " ".join(sorted(scopes))
