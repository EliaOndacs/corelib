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


import threading

# Dictionary to hold active timeouts
__timeouts__ = {}


def setTimeout(callback, delay):
    """Mimics JavaScript's setTimeout."""
    global __timeouts__
    timer = threading.Timer(delay / 1000, callback)
    timer.start()

    # Store the timer in the timeouts dictionary
    timeout_id = id(timer)  # Use the timer's id as a unique identifier
    __timeouts__[timeout_id] = timer

    return timeout_id


def clearTimeout(timeout_id):
    """Mimics JavaScript's clearTimeout."""
    global __timeouts__
    timer = __timeouts__.pop(timeout_id, None)  # Remove the timer from the dictionary
    if timer is not None:
        timer.cancel()  # Cancel the timer if it exists
