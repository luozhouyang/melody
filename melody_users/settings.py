from typing import Union

from dynaconf import Dynaconf


class OAuth2Settings(Dynaconf):
    """OAuth2 settings"""

    def __init__(self, wrapped=None, **kwargs):
        super().__init__(wrapped, **kwargs)

    def get_provider(self, provider_id: str) -> Union[dict, None]:
        """Get provider settings"""
        for provider in self.oauth.providers:
            if provider.id == provider_id:
                return provider
        return None

    def get_client(self, provider_id: str, client_id: str = None) -> Union[dict, None]:
        """Get client settings"""
        if client_id is not None:
            for client in self.oauth.clients:
                if client.id == client_id and client.provider == provider_id:
                    return client
        else:
            for client in self.oauth.clients:
                if client.provider == provider_id:
                    return client
        return None


oauth2_settings = OAuth2Settings(
    settings_files=["oauth.toml"],
    environments=True,
)
