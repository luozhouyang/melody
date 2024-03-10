import abc
import uuid
from typing import Union

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .tables import OAuth2Client, OAuth2Provider


class AbstractOAuth2ProviderService(abc.ABC):
    """Abstract OAuth provider service."""

    @abc.abstractmethod
    async def get_provider(self, provider: str) -> Union[OAuth2Provider, None]:
        raise NotImplementedError()


class AbstractOAuth2ClientService(abc.ABC):
    """Abstract OAuth client service."""

    @abc.abstractmethod
    async def get_client(self, provider: str, client_id: str) -> Union[OAuth2Client, None]:
        raise NotImplementedError()


class DatabaseOAuth2ProviderService(AbstractOAuth2ProviderService):
    """OAuth provider service."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def get_provider(self, provider: str) -> Union[OAuth2Provider, None]:
        """Get OAuth provider.

        Parameters:
        -----------
        provider: str
            The name of the provider.

        Returns:
        --------
        OAuth2Provider
            The OAuth provider, or None if not found.
        """
        async with AsyncSession(self._engine) as sess:
            statememt = select(OAuth2Provider).where(OAuth2Provider.name == provider)
            results = sess.exec(statememt).one_or_none()
            if not results:
                return None
            return results


class DatabaseOAuth2ClientService(AbstractOAuth2ClientService):
    """OAuth client service."""

    def __init__(self, engine: AsyncEngine, tenant_id: uuid.UUID) -> None:
        self._engine = engine
        self._tenant_id = tenant_id

    async def get_client(self, provider: str, client_id: str) -> Union[OAuth2Client, None]:
        """Get OAuth client.

        Parameters:
        -----------
        provider: str
            The name of the provider.
        client_id: str
            The client id of the oauth providr

        Returns:
        --------
        OAuth2Client
            The OAuth client, or None if not found.
        """
        async with AsyncSession(self._engine) as sess:
            statement = select(OAuth2Client).where(
                OAuth2Client.provider == provider,
                OAuth2Client.client_id == client_id,
                OAuth2Client.tenant_id == self._tenant_id,
            )
            client = sess.exec(statement).one_or_none()
            if not client:
                return None
            return client
