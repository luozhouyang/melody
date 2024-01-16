from urllib.parse import urlparse

from melody import oauth2_client, provider_repository, states_repository


def test_authorize():
    provider_repository.register_oauth2_provider(
        id="test_provider",
        authorize_uri="https://test_provider.com/authorize",
        token_uri="https://test_provider.com/token",
    )
    print(provider_repository._providers)

    url = oauth2_client.authorize(
        client_id="test",
        redirect_uri="https://melody.com",
        scope="test",
        provider_id="test_provider",
        response_type="code",
    )

    parsed_url = urlparse(url)
    assert "https" == parsed_url.scheme
    assert "test_provider.com" == parsed_url.netloc
    assert "/authorize" == parsed_url.path
    assert "client_id=test" in parsed_url.query
    assert "redirect_uri=https%3A%2F%2Fmelody.com" in parsed_url.query
    assert "scope=test" in parsed_url.query
    assert "response_type=code" in parsed_url.query

    assert "state=" in parsed_url.query
