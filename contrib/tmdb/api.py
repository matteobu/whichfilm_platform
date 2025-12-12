"""TMDB API client for fetching movie information."""

import logging

import requests
from decouple import config

from contrib.base import BaseClient, NetworkError, ValidationError

logger = logging.getLogger(__name__)


class TMDBClient(BaseClient):
    """
    TMDB (The Movie Database) API client.

    Fetches movie information from TMDB API v3.
    """

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key=None):
        """
        Initialize TMDB client.

        Args:
            api_key (str, optional): TMDB API key. Defaults to TMDB_API_KEY env var.
        """
        self.api_key = api_key or config("TMDB_API_KEY", default=None)
        super().__init__()

    def _validate_config(self):
        """Validate that the client is properly configured."""
        if not self.api_key:
            raise ValidationError(
                "TMDB API key is required. Set TMDB_API_KEY environment variable."
            )

    def _make_request(self, endpoint, params=None):
        """
        Make a request to TMDB API.

        Args:
            endpoint (str): API endpoint (e.g., '/search/movie')
            params (dict, optional): Query parameters

        Returns:
            dict: API response data

        Raises:
            NetworkError: If request fails
        """
        if params is None:
            params = {}

        # Add API key to params
        params["api_key"] = self.api_key

        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"TMDB API request failed: {e}") from e

    def search_movie(self, title, year=None):
        """
        Search for a movie by title.

        Args:
            title (str): Movie title to search for
            year (int, optional): Release year to narrow search

        Returns:
            dict or None: Movie data if found, None otherwise

        Movie data includes:
            - id: TMDB ID
            - title: Movie title
            - release_date: Release date (YYYY-MM-DD)
            - overview: Movie description
            - poster_path: Poster image path
            - backdrop_path: Backdrop image path
            - imdb_id: IMDb ID (requires external_ids endpoint)
        """
        try:
            params = {
                "query": title,
                "include_adult": False,
            }

            if year:
                params["year"] = year

            # Search for the movie
            response = self._make_request("/search/movie", params)

            if not response.get("results"):
                logger.info(f"No results found for '{title}'")
                return None

            # Get the first (most relevant) result
            movie = response["results"][0]

            # Try to get IMDb ID (requires additional request)
            imdb_id = self._get_imdb_id(movie["id"])
            movie["imdb_id"] = imdb_id

            logger.info(
                f"Found movie: {movie.get('title')} (TMDB ID: {movie.get('id')})"
            )
            return movie

        except NetworkError as e:
            logger.error(f"Error searching for '{title}': {e}")
            raise

    def _get_imdb_id(self, tmdb_id):
        """
        Get IMDb ID from TMDB movie ID.

        Args:
            tmdb_id (int): TMDB movie ID

        Returns:
            str or None: IMDb ID if found, None otherwise
        """
        try:
            response = self._make_request(f"/movie/{tmdb_id}/external_ids")
            return response.get("imdb_id")
        except NetworkError as e:
            logger.warning(f"Could not fetch IMDb ID for TMDB ID {tmdb_id}: {e}")
            return None

    def get_data(self, **kwargs):
        """
        Fetch data from TMDB API.

        Args:
            **kwargs: API-specific parameters (query, year, etc.)

        Returns:
            dict: Movie data from TMDB
        """
        title = kwargs.get("query") or kwargs.get("title")
        year = kwargs.get("year")

        if not title:
            raise ValidationError("'title' or 'query' parameter is required")

        return self.search_movie(title, year)
