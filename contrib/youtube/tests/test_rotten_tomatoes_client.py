"""
Tests for RottenTomatoesClient.

Organized by method type:
- Function tests: _clean_title, _extract_year
- API tests: _fetch_videos (with mocking)
- Integration tests: get_data (full pipeline)
"""
import pytest
from contrib.youtube.api import RottenTomatoesClient


class TestRottenTomatoesClientCleanTitle:
    """Test suite for RottenTomatoesClient._clean_title() method."""

    def test_clean_title__extracts_movie_name(self):
        """Test that _clean_title removes trailer format and year."""
        client = RottenTomatoesClient()

        result = client._clean_title("The Lord of the Rings Official Trailer #1 (2025)")

        assert result == "The Lord of the Rings"

    def test_clean_title__with_multiple_words(self):
        """Test title with multiple words."""
        client = RottenTomatoesClient()

        result = client._clean_title("Dune Part Two Official Trailer #1 (2024)")

        assert result == "Dune Part Two"

    def test_clean_title__skips_teaser(self):
        """Test that teasers return None (should be skipped)."""
        client = RottenTomatoesClient()

        result = client._clean_title("Avatar Official Teaser (2025)")

        assert result is None

    def test_clean_title__no_trailer_pattern(self):
        """Test title without trailer pattern returns None."""
        client = RottenTomatoesClient()

        result = client._clean_title("Random YouTube Video Title")

        assert result is None


class TestRottenTomatoesClientFetchVideos:
    """Test suite for RottenTomatoesClient._fetch_videos() method (with mocking)."""

    # TODO: Add tests with @patch for yt-dlp mocking
    pass


class TestRottenTomatoesClientGetData:
    """Test suite for RottenTomatoesClient.get_data() - full integration tests."""

    # TODO: Add integration tests for full pipeline
    pass
