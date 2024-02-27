import logging
from typing import Dict

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OAuth2Provider(BaseModel):
    id: str
    authorize_uri: str
    token_uri: str


class OAuth2ProviderRepository:
    """OAuth2 provider repository"""

    def __init__(self) -> None:
        self._providers: Dict[str, OAuth2Provider] = {}

    def get_provider(self, id: str) -> OAuth2Provider:
        """Get a OAuth2 provider by id.

        Parameters
        ----------
        id : str
            OAuth2 provider id

        Returns
        -------
        OAuth2Provider
            OAuth2 provider

        Raises
        ------
        ValueError
            If id is None or empty.

        Examples
        --------
        >>> provider_repository.get_provider("github")
        """
        return self._providers.get(id, None)

    def register_oauth2_provider(self, id, authorize_uri, token_uri):
        """Register a new OAuth2 provider.

        Parameters
        ----------
        id : str
            OAuth2 provider id
        authorize_uri : str
            OAuth2 provider authorize uri
        token_uri : str
            OAuth2 provider token uri

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If id, authorize_uri or token_uri is None or empty.

        Examples
        --------
        >>>
        >>> @provider_repository.register_oauth2_provider
        ... def func():
        ...     pass

        """

        provider = OAuth2Provider(id=id, authorize_uri=authorize_uri, token_uri=token_uri)
        if provider.id in self._providers:
            logger.warning(f"OAuth2 provider {provider.id} is already registered, replaced by custom one.")
        self._providers[id] = provider


provider_repository = OAuth2ProviderRepository()
