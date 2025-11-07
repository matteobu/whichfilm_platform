"""Base client class for all external integrations."""

from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Abstract base class for all external service clients.
    Subclasses should implement the specific API interaction logic.
    """

    def __init__(self):
        """Initialize the client."""
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """
        Validate that the client is properly configured.

        Subclasses should override this to check for required
        environment variables, API keys, etc.

        Should raise ValidationError if configuration is invalid.
        """
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """
        Fetch data from the external service.

        Subclasses must implement their specific data fetching logic.
        """
        pass
