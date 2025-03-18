"""
Sing-Box API Client module.
Provides an async client for interacting with Sing-Box HTTP API.
"""

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx


class SingBoxAPIClient:
    """Async client for interacting with Sing-Box API.

    Args:
        base_url: The base URL of the Sing-Box API
        token: The API authentication token
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:9090",
        token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.timeout = timeout
        if not self._health_check():
            raise ValueError(f"Invalid to initialize client: {self.base_url}")

    def _health_check(self) -> bool:
        """Check if the API is reachable.

        Returns:
            True if the API is reachable, False otherwise
        """
        try:
            response = httpx.get(
                f"{self.base_url}", timeout=self.timeout, headers=self.headers
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make a request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: URL parameters
            data: Request body data

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            if response.content:
                return dict(response.json())
            return {}

    async def traffic_stream(self) -> AsyncGenerator[dict[str, Any], None]:
        """
        Get traffic statistics as a stream of updates.

        Yields:
            Dictionary containing traffic data (up/down in B/s)
        """
        url = f"{self.base_url}/traffic"

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET", url, headers=self.headers, timeout=None
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():  # Skip empty lines
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue

    async def memory_stream(self) -> AsyncGenerator[dict[str, Any], None]:
        """
        Get memory statistics as a stream of updates.

        Yields:
            Dictionary containing memory data (inuse/total in bytes)
        """
        url = f"{self.base_url}/memory"

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET", url, headers=self.headers, timeout=None
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():  # Skip empty lines
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue

    async def get_connections(self) -> dict[str, Any]:
        """
        Get current connections.

        Returns:
            Dictionary containing active connections
        """
        return await self._make_request("GET", "/connections")

    async def close_connection(self, connection_id: str) -> dict[str, Any]:
        """
        Close a specific connection.

        Args:
            connection_id: ID of the connection to close

        Returns:
            Response from the API
        """
        return await self._make_request("DELETE", f"/connections/{connection_id}")

    async def close_all_connections(self) -> dict[str, Any]:
        """
        Close all connections.

        Returns:
            Response from the API
        """
        return await self._make_request("DELETE", "/connections")

    async def get_groups(self) -> dict[str, Any]:
        """
        Get all policy groups.

        Returns:
            Dictionary containing policy groups information
        """
        return await self._make_request("GET", "/group")

    async def get_group(self, group_name: str) -> dict[str, Any]:
        """
        Get information about a specific policy group.

        Args:
            group_name: Name of the policy group

        Returns:
            Dictionary containing the policy group information
        """
        return await self._make_request("GET", f"/group/{group_name}")

    async def test_group_delay(
        self,
        group_name: str,
        url: str = "https://cp.cloudflare.com/generate_204",
        timeout: int = 5000,
    ) -> dict[str, Any]:
        """
        Test delay for all proxies in a policy group.

        Args:
            group_name: Name of the policy group
            url: URL to test latency against
            timeout: Timeout in milliseconds

        Returns:
            Dictionary containing delay test results
        """
        params = {"url": url, "timeout": timeout}
        return await self._make_request(
            "GET", f"/group/{group_name}/delay", params=params
        )

    async def test_proxy_delay(
        self,
        proxy_name: str,
        url: str = "https://cp.cloudflare.com/generate_204",
        timeout: int = 5000,
    ) -> dict[str, Any]:
        """
        Test delay for a specific proxy.

        Args:
            proxy_name: Name of the proxy
            url: URL to test latency against
            timeout: Timeout in milliseconds

        Returns:
            Dictionary containing delay test results
        """
        params = {"url": url, "timeout": timeout}
        return await self._make_request(
            "GET", f"/proxies/{proxy_name}/delay", params=params
        )

    async def select_proxy(self, proxy_name: str, selected: str) -> dict[str, Any]:
        """
        Select a proxy for a selector proxy group.

        Args:
            proxy_name: Name of the proxy selector
            selected: Name of the proxy to select

        Returns:
            Response from the API
        """
        data = {"name": selected}
        return await self._make_request("PUT", f"/proxies/{proxy_name}", data=data)

    async def get_version(self) -> dict[str, Any]:
        """
        Get Sing-Box version.

        Returns:
            Dictionary containing version information
        """
        return await self._make_request("GET", "/version")
