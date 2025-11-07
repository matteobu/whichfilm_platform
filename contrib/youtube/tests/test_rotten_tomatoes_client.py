"""
Tests for RottenTomatoesClient.
"""
import pytest
from contrib.youtube.api import RottenTomatoesClient


class TestRottenTomatoesClientCleanTitle:
    """Test suite for RottenTomatoesClient._clean_title()"""

    def test_clean_title_extracts_movie_name(self):
        """Test that _clean_title removes trailer format and year."""
        client = RottenTomatoesClient()

        result = client._clean_title("The Lord of the Rings Official Trailer #1 (2025)")

        assert result == "The Lord of the Rings"

    def test_clean_title_with_multiple_words(self):
        """Test title with multiple words."""
        client = RottenTomatoesClient()

        result = client._clean_title("Dune Part Two Official Trailer #1 (2024)")

        assert result == "Dune Part Two"

    def test_clean_title_skips_teaser(self):
        """Test that teasers return None (should be skipped)."""
        client = RottenTomatoesClient()

        result = client._clean_title("Avatar Official Teaser (2025)")

        assert result is None

    def test_clean_title_no_trailer_pattern(self):
        """Test title without trailer pattern returns None."""
        client = RottenTomatoesClient()

        result = client._clean_title("Random YouTube Video Title")

        assert result is None
