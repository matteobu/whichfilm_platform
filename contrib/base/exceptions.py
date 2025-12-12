"""Common exceptions for contrib integrations."""


class ClientError(Exception):
    """Base exception for client errors."""

    pass


class RateLimitError(ClientError):
    """Raised when rate limit is exceeded."""

    pass


class ValidationError(ClientError):
    """Raised when input validation fails."""

    pass


class NetworkError(ClientError):
    """Raised when network request fails."""

    pass


class NotFoundError(ClientError):
    """Raised when resource is not found."""

    pass
