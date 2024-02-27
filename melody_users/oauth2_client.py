import logging
from typing import List, Optional, Union
from uuid import uuid4

from furl import furl
from pydantic import BaseModel

from .oauth2_providers import provider_repository

logger = logging.getLogger(__name__)


class OAuth2RegisteredClient(BaseModel):
    client_id: str
    client_secret: str
    provider: str


class OAuth2ClientRepository:
    """OAuth2 client repository"""

    def __init__(self) -> None:
        super().__init__()
        self._clients = {}

    def register_oauth2_client(self, client_id: str, client_secret: str, provider: str) -> OAuth2RegisteredClient:
        """Register a OAuth2 client for the provider to repository.

        Parameters
        ----------
        client_id: str
            The client id of the OAuth2 client.
        client_secret: str
            The client secret of the OAuth2 client.
        provider: str
            The provider id.

        Returns
        -------
        OAuth2Client
            The OAuth2 client registered to repository.

        Raises
        ------
        ValueError
            If client_id, client_secret or provider is None or empty.

        Examples
        --------
        >>> oauth2_client_repo = OAuth2ClientRepository()
        >>> oauth2_client_repo.register_oauth2_client(
                client_id="your_google_client_id", client_secret="your_google_client_secret", provider="google")
        >>> oauth2_client_repo.register_oauth2_client(
                client_id="your_github_client_id", client_secret="your_github_client_secret", provider="github")
        """
        if not client_id:
            raise ValueError(f"client_id is required.")
        if not client_secret:
            raise ValueError(f"client_secret is required.")
        if not provider:
            raise ValueError(f"provider is required.")
        client = OAuth2RegisteredClient(client_id=client_id, client_secret=client_secret, provider=provider)
        provider_clients = self._clients.get(client.provider, None)
        if not provider_clients:
            provider_clients = {}
        if client_id in provider_clients:
            logger.warning(f"OAuth2 client {client_id} for {provider} already registered, replaced by custom one.")
        provider_clients[client_id] = client
        self._clients[provider] = provider_clients
        return client

    def remove_oauth2_client(self, client_id: str, provider: Optional[str] = None) -> OAuth2RegisteredClient:
        """Remove a OAuth2 client for the repository.

        Parameters
        ----------
        client_id: str
            The client id of the OAuth2 client.
        provider: str
            The provider id. If None, remove all clients for the repository whose id equals to client_id, ignores the provider id.

        Returns
        -------
        OAuth2Client
            The OAuth2 client removed from repository. None if not found.

        Raises
        ------
        ValueError
            If client_id is None or empty.

        Examples
        --------
        >>> oauth2_client_repo = OAuth2ClientRepository()
        >>> oauth2_client_repo.remove_oauth2_client(
                client_id="your_google_client_id", provider="google")
        >>> oauth2_client_repo.remove_oauth2_client(
                client_id="your_github_client_id", provider="github")
        >>> oauth2_client_repo.remove_oauth2_client(client_id="your_google_client_id")
        """
        if provider:
            provider_clients = self._clients.get(provider, None)
            if provider_clients is None:
                provider_clients = {}
            return provider_clients.pop(client_id, None)
        c = None
        for p, clients in self._clients.items():
            c = clients.pop(client_id, None)
            if c is not None:
                return c
        return c

    def get_oauth2_client(self, client_id: str, provider: Optional[str] = None) -> OAuth2RegisteredClient:
        """Get a OAuth2 client from the repository.

        Parameters
        ----------
        client_id: str
            The client id of the OAuth2 client.
        provider: str
            The provider id. If None, get all clients for the repository whose id equals to client_id, ignores the provider id.

        Returns
        -------
        OAuth2Client
            The OAuth2 client found in repository. None if not found.

        Examples
        --------
        >>> oauth2_client_repo = OAuth2ClientRepository()
        >>> oauth2_client_repo.get_oauth2_client(
                client_id="your_google_client_id", provider="google")
        >>> oauth2_client_repo.get_oauth2_client(
                client_id="your_github_client_id", provider="github")
        >>> oauth2_client_repo.get_oauth2_client(client_id="your_google_client_id")

        """
        if provider:
            provider_clients = self._clients.get(provider, None)
            if provider_clients is None:
                provider_clients = {}
            return provider_clients.get(client_id, None)
        for p, clients in self._clients.items():
            c = clients.get(client_id, None)
            if c is not None:
                return c
        return None


client_repository = OAuth2ClientRepository()


class OAuth2State(BaseModel):
    id: str
    client_id: str
    provider: str


class OAuth2StateRepository:
    """OAuth2 state repository"""

    def __init__(self) -> None:
        self._states = {}

    def save(self, state: OAuth2State, **kwargs) -> None:
        """Save the state to repository.

        Parameters
        ----------
        state: OAuth2State
            The state to save.
        **kwargs
            Additional parameters for the provider.
        Returns
        -------
        None

        Raises
        ------
        ValueError
            If state is None.

        Examples
        --------
        >>> oauth2_state_repo = OAuth2StateRepository()
        >>> state = OAuth2State(
                id="uuid",
                client_id="your_google_client_id",
                redirect_uri="your_redirect_uri",
                provider="google",
                **kwargs")
        >>> oauth2_state_repo.save(state)
        """
        print("state: ", state)
        if not state:
            raise ValueError(f"state is required.")
        self._states[state.id] = state

    def delete(self, id: str) -> Union[OAuth2State, None]:
        """Delete the state from repository.

        Parameters
        ----------
        id: str
            The id of the state to delete.

        Returns
        -------
        OAuth2State
            The state deleted from repository. None if not found.

        Raises
        ------
        ValueError
            If id is None or empty.

        Examples
        --------
        >>> oauth2_state_repo = OAuth2StateRepository()
        >>> oauth2_state_repo.delete(id="your_state_id")

        """
        if not id:
            raise ValueError(f"id is required.")
        return self._states.pop(id, None)


states_repository = OAuth2StateRepository()


def _normalize_scope(scope: Union[str, List[str]]) -> str:
    if isinstance(scope, list):
        scope = [x.strip() for x in scope if x.strip()]
        scope = " ".join(sorted(scope))
        return scope
    if isinstance(scope, str):
        scope = [x.strip() for x in scope.split("\\s+") if x.strip()]
        scope = " ".join(sorted(scope))
        return scope
    raise ValueError(f"Unrecoginzed scope: {scope}")


def authorize(
    client_id: str,
    redirect_uri: str,
    scope: Union[str, List[str]],
    provider_id: str,
    response_type: str = "code",
    **kwargs,
) -> str:
    if not client_id:
        raise ValueError(f"client_id is required.")
    if not redirect_uri:
        raise ValueError(f"redirect_uri is required.")
    if not provider_id:
        raise ValueError(f"provider_id is required.")
    scope = _normalize_scope(scope)
    if not scope:
        raise ValueError(f"scope is required.")

    oauth_provider = provider_repository.get_provider(id=provider_id)
    if not oauth_provider:
        raise ValueError(f"provider_id is not found: {provider_id}")

    state_id = str(uuid4())
    state = OAuth2State(id=state_id, client_id=client_id, provider=provider_id)
    states_repository.save(state)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": response_type,
        "state": state_id,
    }
    url = furl(oauth_provider.authorize_uri)
    url.args = params
    return str(url)
