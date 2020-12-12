"""
Connectors module: Provide authentication implementation
"""

from typing import Tuple

import aiohttp

from .core import BaseSalesforceStreaming


class BaseConnector(BaseSalesforceStreaming):
    """
    Base class for all sf connectors.

    :param client_id: OAuth2 client Id (mandatory)
    :param client_secret: Oauth2 client secret (mandatory)
    :param login_connector: aiohttp connector used during connection.
        Mainly used for test purpose.

    See :class:`.BaseSalesforceStreaming` for other keywords arguments.
    """

    def __init__(
        self,
        *,
        client_id: str = None,
        client_secret: str = None,
        login_connector: aiohttp.BaseConnector = None,
        **kwargs
    ):
        if any(v is None for v in (client_id, client_secret)):
            raise TypeError("All credentials arguments are mandatory")

        self.login_connector = login_connector
        self.credentials = {"client_id": client_id, "client_secret": client_secret}
        super().__init__(**kwargs)

    async def fetch_token(self) -> Tuple[str, str]:
        # use a temporary session only to fetch token because client session
        # does not seems to allow update default headers on a already created
        # session
        async with aiohttp.ClientSession(
            connector=self.login_connector, headers=self.base_header, loop=self.loop
        ) as session:
            async with session.post(self.token_url, data=self.credentials) as resp:
                data = await resp.json()

        assert data.get("token_type") == "Bearer"
        instance_url = data["instance_url"]
        access_token = data["access_token"]

        return access_token, instance_url


class PasswordSalesforceStreaming(BaseConnector):
    """
    Create a SF streaming manager with password flow connection.

    Main arguments are connection credentials:

    :param username: User login name
    :param password: User password

    See :class:`.BaseConnector` for other keywords arguments.
    """

    def __init__(self, *, username: str = None, password: str = None, **kwargs):
        if any(v is None for v in (username, password)):
            raise TypeError("All credentials arguments are mandatory")

        super().__init__(**kwargs)
        # Credentials used to fetch access token
        self.credentials.update(
            {"grant_type": "password", "username": username, "password": password}
        )


class RefreshTokenSalesforceStreaming(BaseConnector):
    """
    Create a SF streaming manager with password refresh token connection.

    Main arguments are connection credentials:

    :param refresh_token: Refresh token

    See :class:`.BaseConnector` for other keywords arguments.
    """

    def __init__(self, *, refresh_token: str = None, **kwargs):
        if refresh_token is None:
            raise TypeError("All credentials arguments are mandatory")

        super().__init__(**kwargs)
        # Credentials used to fetch access token
        self.credentials.update(
            {"grant_type": "refresh_token", "refresh_token": refresh_token}
        )
