"""TMDB API client for fetching movie information."""

import os
import requests

from contrib.base import BaseClient, ValidationError, NetworkError


class TMDBClient(BaseClient):
    """
    TMDB (The Movie Database) API client.

    Fetches movie information from TMDB API.
    """

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key=None):
        """
        Initialize TMDB client.

        Args:
            api_key (str, optional): TMDB API key. Defaults to TMDB_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        super().__init__()

    def _validate_config(self):
        """Validate that the client is properly configured."""
        if not self.api_key:
            raise ValidationError(
                "TMDB API key is required. Set TMDB_API_KEY environment variable."
            )

    def get_data(self, **kwargs):
        """
        Fetch data from TMDB API.

        Args:
            **kwargs: API-specific parameters

        Returns:
            dict: Movie data from TMDB
        """
        raise NotImplementedError("TMDB client is not yet implemented")
