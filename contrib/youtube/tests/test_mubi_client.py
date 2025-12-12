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

    @pytest.fixture
    def client(self):
        """Fixture: MubiClient instance for testing."""
        return MubiClient()

    @pytest.mark.parametrize(
        "input_title,expected_output",
        [
            ("DUNE | Official Trailer #1", "DUNE"),
            (
                "BLADE RUNNER 2049 | Official Trailer | In Cinemas Now",
                "BLADE RUNNER 2049",
            ),
            ("OPPENHEIMER | Official Teaser (2023)", None),
            ("Random YouTube Video Title", None),
        ],
    )
    def test_clean_title(self, client, input_title, expected_output):
        """Test _clean_title with various input formats."""
        result = client._clean_title(input_title)
        assert result == expected_output


class TestMubiClientFetchVideos:
    """Test suite for MubiClient._fetch_videos() method (with mocking)."""

    def test_fetch_videos__success(self, mubi_client_mocked):
        """Test that _fetch_videos extracts videos correctly."""
        result = mubi_client_mocked._fetch_videos()

        # Assert we got a list with correct number of videos
        assert len(result) == 3
        assert result[0]["title"] == "DUNE | Official Trailer #1"
        assert result[0]["video_id"] == "mubi_abc123"
        assert result[1]["video_id"] == "mubi_xyz789"
        assert result[2]["video_id"] == "mubi_skip123"


class TestMubiClientExtractTitleAndId:
    """Test suite for MubiClient._extract_title_and_id() method."""

    @pytest.fixture
    def client(self):
        """Fixture: MubiClient instance for testing."""
        return MubiClient()

    @pytest.mark.parametrize(
        "raw_videos,expected_count,expected_titles",
        [
            (
                # Filters teasers
                [
                    {
                        "title": "DUNE | Official Trailer #1",
                        "video_id": "mubi_abc123",
                        "description": "Sci-fi epic",
                    },
                    {
                        "title": "BLADE RUNNER 2049 | Official Trailer | In Cinemas Now",
                        "video_id": "mubi_xyz789",
                        "description": "Sci-fi masterpiece",
                    },
                    {
                        "title": "OPPENHEIMER | Official Teaser (2023)",
                        "video_id": "mubi_skip123",
                        "description": "Teaser (should be skipped)",
                    },
                ],
                2,
                ["DUNE", "BLADE RUNNER 2049"],
            ),
            (
                # Preserves original title
                [
                    {
                        "title": "ARRIVAL | Official Trailer #1",
                        "video_id": "mubi_vid123",
                        "description": "Sci-fi drama",
                    },
                ],
                1,
                ["ARRIVAL"],
            ),
        ],
    )
    def test_extract_title_and_id(
        self, client, raw_videos, expected_count, expected_titles
    ):
        """Test _extract_title_and_id with various video lists."""
        result = client._extract_title_and_id(raw_videos)

        assert len(result) == expected_count
        for i, expected_title in enumerate(expected_titles):
            assert result[i]["title"] == expected_title

        # Additional checks for first test case (filters teasers)
        if expected_count == 2:
            assert result[0]["video_id"] == "mubi_abc123"
            assert result[1]["video_id"] == "mubi_xyz789"
            assert result[1]["year"] is None

        # Additional checks for second test case (preserves original title)
        if expected_count == 1 and expected_titles[0] == "ARRIVAL":
            assert result[0]["original_title"] == "ARRIVAL | Official Trailer #1"
            assert result[0]["video_id"] == "mubi_vid123"


class TestMubiClientGetData:
    """Test suite for MubiClient.get_data() - full integration tests."""

    def test_get_data__returns_processed_videos(self, mubi_client_mocked):
        """Test that get_data returns fully processed video list."""
        result = mubi_client_mocked.get_data()

        # Verify structure
        assert isinstance(result, list)
        assert len(result) == 2  # 3 videos, 1 filtered (teaser)

        # Verify first video
        assert result[0]["title"] == "DUNE"
        assert result[0]["original_title"] == "DUNE | Official Trailer #1"
        assert result[0]["video_id"] == "mubi_abc123"
        assert result[0]["year"] is None  # MUBI format doesn't have year

        # Verify second video
        assert result[1]["title"] == "BLADE RUNNER 2049"
        assert (
            result[1]["original_title"]
            == "BLADE RUNNER 2049 | Official Trailer | In Cinemas Now"
        )
        assert result[1]["video_id"] == "mubi_xyz789"
        assert result[1]["year"] is None

    def test_get_data__filters_teasers(self, mubi_client_mocked):
        """Test that teaser videos are filtered out."""
        result = mubi_client_mocked.get_data()

        # Should only have 2 videos (teaser filtered)
        assert len(result) == 2

        # Verify no teaser in results
        titles = [v["title"] for v in result]
        assert "OPPENHEIMER" not in titles  # Teaser was filtered

    def test_get_data__filters_coming_soon(self, mubi_client_mocked):
        """Test that 'Coming Soon' announcements are filtered."""
        raw_videos = [
            {
                "title": "DUNE | Official Trailer #1",
                "video_id": "mubi_abc123",
                "description": "Sci-fi epic",
            },
            {
                "title": "UPCOMING FILM | Coming Soon",
                "video_id": "mubi_upcoming",
                "description": "Coming soon",
            },
        ]

        result = mubi_client_mocked._extract_title_and_id(raw_videos)

        # Should only have 1 video
        assert len(result) == 1
        assert result[0]["title"] == "DUNE"

    def test_get_data__handles_pipe_separator(self, mubi_client_mocked):
        """Test correct extraction with pipe separator."""
        result = mubi_client_mocked.get_data()

        # Pipes should be removed from titles
        for video in result:
            assert "|" not in video["title"]
            # But should be in original
            assert "|" in video["original_title"]

    def test_get_data__uppercase_titles(self, mubi_client_mocked):
        """Test that uppercase MUBI titles are preserved."""
        result = mubi_client_mocked.get_data()

        # MUBI uses uppercase titles
        assert result[0]["title"] == "DUNE"  # Uppercase
        assert result[1]["title"] == "BLADE RUNNER 2049"  # Uppercase

    def test_get_data__handles_multiple_pipes(self, mubi_client_mocked):
        """Test extraction with multiple pipes in title."""
        raw_videos = [
            {
                "title": "MOVIE NAME | Official Trailer #1 | In Cinemas Now | More Info",
                "video_id": "mubi_test",
                "description": "Test",
            }
        ]

        result = mubi_client_mocked._extract_title_and_id(raw_videos)

        # Should extract everything before first pipe
        assert result[0]["title"] == "MOVIE NAME"
        assert (
            result[0]["original_title"]
            == "MOVIE NAME | Official Trailer #1 | In Cinemas Now | More Info"
        )

    def test_get_data__extracts_all_required_fields(self, mubi_client_mocked):
        """Test that all required fields are present."""
        result = mubi_client_mocked.get_data()

        for video in result:
            # All these fields must exist
            assert "title" in video
            assert "original_title" in video
            assert "video_id" in video
            assert "year" in video

            # Verify non-empty values where expected
            assert video["title"] != ""
            assert video["original_title"] != ""
            assert video["video_id"] != ""

    def test_get_data__year_is_none_for_mubi(self, mubi_client_mocked):
        """Test that MUBI titles don't extract year (format doesn't include it)."""
        result = mubi_client_mocked.get_data()

        # All MUBI videos should have year=None
        for video in result:
            assert video["year"] is None

    def test_get_data__integration_full_pipeline(self, mubi_client_mocked):
        """Test the full pipeline: fetch → extract → clean → return."""
        # This simulates: YoutubeDL → _fetch_videos → _extract_title_and_id → get_data
        result = mubi_client_mocked.get_data()

        # Should complete without errors
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

        # Each result should be properly processed
        for video in result:
            # Should have gone through _clean_title successfully
            assert "|" not in video["title"]  # Pipes removed
            assert "Official Trailer" not in video["title"]  # Trailer format removed
            # Should still have the raw version
            assert "|" in video["original_title"]

    def test_get_data__preserves_video_order(self, mubi_client_mocked):
        """Test that videos maintain their original order."""
        result = mubi_client_mocked.get_data()

        # First video should be DUNE
        assert result[0]["title"] == "DUNE"
        # Second should be BLADE RUNNER (teaser filtered)
        assert result[1]["title"] == "BLADE RUNNER 2049"

    def test_get_data__empty_list_returns_empty(self, monkeypatch):
        """Test that empty YouTube response returns empty list."""
        from unittest.mock import MagicMock

        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {"entries": []}
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None

        monkeypatch.setattr(
            "contrib.youtube.api.YoutubeDL", lambda *args, **kwargs: mock_instance
        )

        client = MubiClient()
        result = client.get_data()

        assert result == []

    def test_get_data__vs_rotten_tomatoes_differences(
        self, mubi_client_mocked, rotten_tomatoes_client_mocked
    ):
        """Test that MUBI client behaves differently from RottenTomatoes client."""
        mubi_result = mubi_client_mocked.get_data()
        rt_result = rotten_tomatoes_client_mocked.get_data()

        # Both should return lists
        assert isinstance(mubi_result, list)
        assert isinstance(rt_result, list)

        # MUBI uses pipe separator, RottenTomatoes doesn't
        if mubi_result:
            assert "|" not in mubi_result[0]["title"]
            assert "|" in mubi_result[0]["original_title"]

        if rt_result:
            assert "|" not in rt_result[0]["title"]
            assert "|" not in rt_result[0]["original_title"]

        # MUBI year is always None, RottenTomatoes extracts year
        if mubi_result:
            assert mubi_result[0]["year"] is None
        if rt_result:
            # RottenTomatoes should have extracted year
            assert rt_result[0]["year"] == 2025
