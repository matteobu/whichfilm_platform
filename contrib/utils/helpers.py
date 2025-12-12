"""Common helper functions for contrib modules."""

import requests

from contrib.base import NetworkError


def safe_request(url, method="GET", timeout=10, **kwargs):
    """
    Make a safe HTTP request with error handling.

    Args:
        url (str): URL to request
        method (str): HTTP method (GET, POST, etc.)
        timeout (int): Request timeout in seconds
        **kwargs: Additional arguments to pass to requests

    Returns:
        requests.Response: Response object

    Raises:
        NetworkError: If request fails
    """
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Request failed for {url}: {e}") from e


def parse_json_safe(response):
    """
    Safely parse JSON from response.

    Args:
        response (requests.Response): Response object

    Returns:
        dict: Parsed JSON data

    Raises:
        NetworkError: If JSON parsing fails
    """
    try:
        return response.json()
    except ValueError as e:
        raise NetworkError(f"Failed to parse JSON: {e}") from e
