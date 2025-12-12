"""Base classes and exceptions for all contrib integrations."""

from .client import BaseClient
from .exceptions import (
    ClientError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "BaseClient",
    "ClientError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
    "NotFoundError",
]
