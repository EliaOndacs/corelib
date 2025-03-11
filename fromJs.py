"a library to mimic api's from javascript :skull:"

import httpx
from typing import Optional, Union, Dict, Any


async def fetch(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
    allow_redirects: bool = True,
) -> httpx.Response:
    """
    Mimics the JavaScript fetch API.

    Args:
        url (str): The URL to fetch.
        method (str): The HTTP method to use (default is 'GET').
        headers (Optional[Dict[str, str]]): Custom headers to send with the request.
        data (Optional[Union[str, Dict[str, Any]]]): The body of the request (for POST, etc.).
        json (Optional[Dict[str, Any]]): JSON data to send in the request body.
        params (Optional[Dict[str, Any]]): URL parameters to include in the request.
        timeout (Optional[float]): Timeout for the request in seconds.
        allow_redirects (bool): Whether to follow redirects (default is True).

    Returns:
        httpx.Response: The response object.
    """
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers=headers,
            data=data,  # type: ignore
            json=json,
            params=params,
            timeout=timeout,
            follow_redirects=allow_redirects,
        )
        return response
