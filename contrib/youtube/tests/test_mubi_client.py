"""
Tests for MubiClient.

Organized by method type:
- Function tests: _clean_title, _extract_year
- API tests: _fetch_videos (with mocking)
- Integration tests: get_data (full pipeline)
"""
import pytest
from contrib.youtube.api import MubiClient


class TestMubiClientCleanTitle:
    """Test suite for MubiClient._clean_title() method."""

    def test_clean_title__extracts_movie_name(self):
        """Test that _clean_title removes trailer format."""
        client = MubiClient()

        result = client._clean_title("DUNE | Official Trailer #1")

        assert result == "DUNE"

    def test_clean_title__with_in_cinemas_now(self):
        """Test title with 'In Cinemas Now' suffix."""
        client = MubiClient()

        result = client._clean_title("BLADE RUNNER 2049 | Official Trailer | In Cinemas Now")

        assert result == "BLADE RUNNER 2049"

    def test_clean_title__skips_teaser(self):
        """Test that teasers return None (should be skipped)."""
        client = MubiClient()

        result = client._clean_title("OPPENHEIMER | Official Teaser (2023)")

        assert result is None

    def test_clean_title__no_official_trailer_pattern(self):
        """Test title without official trailer pattern returns None."""
        client = MubiClient()

        result = client._clean_title("Random YouTube Video Title")

        assert result is None


class TestMubiClientFetchVideos:
    """Test suite for MubiClient._fetch_videos() method (with mocking)."""

    # TODO: Add tests with @patch for yt-dlp mocking
    pass


class TestMubiClientGetData:
    """Test suite for MubiClient.get_data() - full integration tests."""

    # TODO: Add integration tests for full pipeline
    pass
