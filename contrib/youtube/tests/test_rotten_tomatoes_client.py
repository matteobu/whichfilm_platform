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

    def test_fetch_videos__success(self, rotten_tomatoes_client_mocked):
        """Test that _fetch_videos extracts videos correctly."""
        result = rotten_tomatoes_client_mocked._fetch_videos()

        # Assert we got a list with correct number of videos
        assert len(result) == 3
        assert result[0]['title'] == 'The Lord of the Rings Official Trailer #1 (2025)'
        assert result[0]['video_id'] == 'abc123'
        assert result[1]['video_id'] == 'xyz789'
        assert result[2]['video_id'] == 'skip123'


class TestRottenTomatoesClientExtractTitleAndId:
    """Test suite for RottenTomatoesClient._extract_title_and_id() method."""

    def test_extract_title_and_id__filters_teasers(self):
        """Test that _extract_title_and_id filters out teaser videos."""
        client = RottenTomatoesClient()

        # Raw videos from API (3 videos, 1 is teaser)
        raw_videos = [
            {
                'title': 'The Lord of the Rings Official Trailer #1 (2025)',
                'video_id': 'abc123',
                'description': 'Official trailer'
            },
            {
                'title': 'Dune Part Two Official Trailer #1 (2024)',
                'video_id': 'xyz789',
                'description': 'Sci-fi epic'
            },
            {
                'title': 'Avatar Official Teaser (2025)',
                'video_id': 'skip123',
                'description': 'Teaser (should be skipped)'
            }
        ]

        result = client._extract_title_and_id(raw_videos)

        # Should only return 2 (teaser filtered out!)
        assert len(result) == 2
        assert result[0]['title'] == "The Lord of the Rings"
        assert result[0]['video_id'] == 'abc123'
        assert result[0]['year'] == 2025
        assert result[1]['title'] == "Dune Part Two"
        assert result[1]['video_id'] == 'xyz789'
        assert result[1]['year'] == 2024

    def test_extract_title_and_id__preserves_original_title(self):
        """Test that original title is preserved in output."""
        client = RottenTomatoesClient()

        raw_videos = [
            {
                'title': 'Inception Official Trailer #2 (2010)',
                'video_id': 'vid123',
                'description': 'Dream thriller'
            }
        ]

        result = client._extract_title_and_id(raw_videos)

        assert len(result) == 1
        assert result[0]['title'] == "Inception"
        assert result[0]['original_title'] == "Inception Official Trailer #2 (2010)"
        assert result[0]['year'] == 2010


class TestRottenTomatoesClientGetData:
    """Test suite for RottenTomatoesClient.get_data() - full integration tests."""

    def test_get_data__returns_processed_videos(self, rotten_tomatoes_client_mocked):
        """Test that get_data returns fully processed video list."""
        result = rotten_tomatoes_client_mocked.get_data()

        # Verify structure
        assert isinstance(result, list)
        assert len(result) == 2  # 3 videos, 1 filtered (teaser)

        # Verify first video
        assert result[0]['title'] == "The Lord of the Rings"
        assert result[0]['original_title'] == "The Lord of the Rings Official Trailer #1 (2025)"
        assert result[0]['video_id'] == "abc123"
        assert result[0]['year'] == 2025

        # Verify second video
        assert result[1]['title'] == "Dune Part Two"
        assert result[1]['original_title'] == "Dune Part Two Official Trailer #1 (2024)"
        assert result[1]['video_id'] == "xyz789"
        assert result[1]['year'] == 2024

    def test_get_data__filters_teasers(self, rotten_tomatoes_client_mocked):
        """Test that teaser videos are filtered out."""
        result = rotten_tomatoes_client_mocked.get_data()

        # Should only have 2 videos (teaser filtered)
        assert len(result) == 2

        # Verify no teaser in results
        titles = [v['title'] for v in result]
        assert "Avatar" not in titles  # Teaser was filtered

    def test_get_data__extracts_all_required_fields(self, rotten_tomatoes_client_mocked):
        """Test that all required fields are present."""
        result = rotten_tomatoes_client_mocked.get_data()

        for video in result:
            # All these fields must exist
            assert 'title' in video
            assert 'original_title' in video
            assert 'video_id' in video
            assert 'year' in video

            # Verify non-empty values where expected
            assert video['title'] != ""
            assert video['original_title'] != ""
            assert video['video_id'] != ""

    def test_get_data__handles_videos_without_year(self, rotten_tomatoes_client_mocked):
        """Test handling of videos where year extraction fails."""
        client = rotten_tomatoes_client_mocked
        raw_video = [{
            'title': 'Movie Official Trailer #1',  # No year
            'video_id': 'test123',
            'description': 'Test'
        }]

        result = client._extract_title_and_id(raw_video)

        assert len(result) == 1
        assert result[0]['title'] == "Movie"
        assert result[0]['year'] is None  # Year should be None, not fail

    def test_get_data__integration_full_pipeline(self, rotten_tomatoes_client_mocked):
        """Test the full pipeline: fetch → extract → clean → return."""
        # This simulates: YoutubeDL → _fetch_videos → _extract_title_and_id → get_data
        result = rotten_tomatoes_client_mocked.get_data()

        # Should complete without errors
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

        # Each result should be properly processed
        for video in result:
            # Should have gone through _clean_title successfully
            assert "Trailer" not in video['title']
            assert "Official" not in video['title']
            # Should still have the raw version
            assert "Trailer" in video['original_title']

    def test_get_data__preserves_video_order(self, rotten_tomatoes_client_mocked):
        """Test that videos maintain their original order."""
        result = rotten_tomatoes_client_mocked.get_data()

        # First video should be Lord of the Rings
        assert result[0]['title'] == "The Lord of the Rings"
        # Second should be Dune (teasers filtered out)
        assert result[1]['title'] == "Dune Part Two"

    def test_get_data__empty_list_returns_empty(self, monkeypatch):
        """Test that empty YouTube response returns empty list."""
        from unittest.mock import MagicMock

        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {'entries': []}
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None

        monkeypatch.setattr(
            'contrib.youtube.api.YoutubeDL',
            lambda *args, **kwargs: mock_instance
        )

        client = RottenTomatoesClient()
        result = client.get_data()

        assert result == []
