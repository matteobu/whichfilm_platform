"""
Shared pytest fixtures for TMDB API tests.
"""

from unittest.mock import MagicMock

import pytest

from contrib.tmdb.api import TMDBClient

# ============================================================================
# Mock TMDB API Response Data
# ============================================================================


@pytest.fixture
def mock_tmdb_search_response():
    """Fixture: Mock TMDB API response for movie search."""
    return {
        "results": [
            {
                "id": 11,
                "title": "Star Wars",
                "release_date": "1977-05-25",
                "overview": "A long time ago in a galaxy far far away...",
                "poster_path": "/6FfCtJ3lGmTKncQQQ9NcZN1YR23.jpg",
                "backdrop_path": "/8X12wXF3v46x9hxjNM2YYcR76Yv.jpg",
            }
        ]
    }


@pytest.fixture
def mock_tmdb_search_empty_response():
    """Fixture: Empty TMDB search response (no results)."""
    return {"results": []}


@pytest.fixture
def mock_tmdb_external_ids_response():
    """Fixture: Mock TMDB external IDs response."""
    return {
        "imdb_id": "tt0076759",
        "tvdb_id": None,
        "facebook_id": None,
    }


@pytest.fixture
def mock_tmdb_client_with_search(monkeypatch, mock_tmdb_search_response):
    """Fixture: TMDBClient with mocked search_movie method."""
    mock_client = MagicMock(spec=TMDBClient)
    mock_client.search_movie.return_value = mock_tmdb_search_response["results"][0]
    return mock_client


@pytest.fixture
def mock_tmdb_client_with_empty_search(monkeypatch, mock_tmdb_search_empty_response):
    """Fixture: TMDBClient with empty search results."""
    mock_client = MagicMock(spec=TMDBClient)
    mock_client.search_movie.return_value = None
    return mock_client
