"""
Integration tests for YouTube clients.

Tests the complete flow:
- Fetch from YouTube API
- Parse and clean titles
- Filter videos
- Return processed data

This tests the public get_data() method which combines all the pieces.
"""


class TestRottenTomatoesClientIntegration:
    """Integration tests for RottenTomatoesClient.get_data() full pipeline."""

    def test_get_data__full_pipeline_with_mocked_api(
        self, rotten_tomatoes_client_mocked
    ):
        """
        Test that get_data() returns filtered and cleaned videos.

        NEEDS:
        - Use rotten_tomatoes_client_mocked fixture
        - Mock returns 3 videos (2 valid trailers + 1 teaser)
        - Call get_data()
        - Verify: Returns only 2 videos (teaser filtered)
        - Verify: Titles are cleaned
        - Verify: Years are extracted
        - Verify: Original titles are preserved

        EXPECTED BEHAVIOR:
        _fetch_videos() → [3 raw videos]
        _extract_title_and_id() → [2 cleaned videos] (teaser filtered)
        Return: [
            {'title': 'The Lord of the Rings', 'year': 2025, 'original_title': '...', 'video_id': 'abc123'},
            {'title': 'Dune Part Two', 'year': 2024, 'original_title': '...', 'video_id': 'xyz789'}
        ]
        """
        pass

    def test_get_data__handles_all_teasers(self, monkeypatch):
        """
        Test that get_data() returns empty list when all videos are teasers.

        NEEDS:
        - Mock API response with only teaser videos
        - Call get_data()
        - Verify: Returns empty list [] (not None)
        - Verify: No exceptions raised

        EXPECTED BEHAVIOR:
        - Should handle edge case gracefully
        - Should return empty list
        """
        pass

    def test_get_data__empty_channel(self, monkeypatch):
        """
        Test that get_data() handles empty YouTube channel.

        NEEDS:
        - Mock API response with no videos
        - Call get_data()
        - Verify: Raises NetworkError (channel has no videos)

        EXPECTED BEHAVIOR:
        - _fetch_videos() should raise NetworkError if no entries
        - Should propagate the error
        """
        pass

    def test_get_data__preserves_video_ids(self, rotten_tomatoes_client_mocked):
        """
        Test that get_data() preserves YouTube video IDs through pipeline.

        NEEDS:
        - Call get_data()
        - Verify: Each video has original video_id from YouTube
        - Verify: video_id not modified during processing

        EXPECTED BEHAVIOR:
        - Should preserve video_id from API response
        - Should not transform or modify video_id
        """
        pass

    def test_get_data__extracts_years_correctly(self, rotten_tomatoes_client_mocked):
        r"""
        Test that get_data() extracts years from titles.

        NEEDS:
        - Mock videos with years in title: "Title (2025)"
        - Call get_data()
        - Verify: year == 2025 for each video

        EXPECTED BEHAVIOR:
        - Should extract year using regex: r'\((\d{4})\)'
        - Should convert to int
        - Should return None if no year found
        """
        pass


class TestMubiClientIntegration:
    """Integration tests for MubiClient.get_data() full pipeline."""

    def test_get_data__full_pipeline_with_mocked_api(self, mubi_client_mocked):
        """
        Test that get_data() returns filtered and cleaned videos for Mubi.

        NEEDS:
        - Use mubi_client_mocked fixture
        - Mock returns 3 videos (2 valid trailers + 1 teaser)
        - Call get_data()
        - Verify: Returns only 2 videos (teaser filtered)
        - Verify: Titles are cleaned (pipes removed)
        - Verify: Original titles are preserved

        EXPECTED BEHAVIOR:
        _fetch_videos() → [3 raw videos]
        _extract_title_and_id() → [2 cleaned videos] (teaser filtered)
        Return: [
            {'title': 'DUNE', 'year': None, 'original_title': 'DUNE | Official Trailer #1', 'video_id': 'mubi_abc123'},
            {'title': 'BLADE RUNNER 2049', 'year': None, 'original_title': '...', 'video_id': 'mubi_xyz789'}
        ]
        """
        pass

    def test_get_data__filters_coming_soon_videos(self, monkeypatch):
        """
        Test that get_data() filters out "Coming Soon" videos for Mubi.

        NEEDS:
        - Mock API response with "Coming Soon" video
        - Call get_data()
        - Verify: "Coming Soon" video is filtered out

        EXPECTED BEHAVIOR:
        - Should skip videos with "Coming Soon" in title
        - Should skip teaser videos
        - Should only return official trailers
        """
        pass

    def test_get_data__handles_pipe_separated_titles(self, mubi_client_mocked):
        """
        Test that get_data() correctly parses Mubi's pipe-separated format.

        NEEDS:
        - Mock video with title: "MOVIE NAME | Official Trailer | Extra Info"
        - Call get_data()
        - Verify: Extracted title is "MOVIE NAME"
        - Verify: Pipes and extra info are removed

        EXPECTED BEHAVIOR:
        - Should extract everything before "| Official Trailer"
        - Should strip whitespace
        - Should preserve case (UPPERCASE for Mubi)
        """
        pass

    def test_get_data__handles_in_cinemas_now_suffix(self, mubi_client_mocked):
        """
        Test that get_data() handles "In Cinemas Now" suffix.

        NEEDS:
        - Mock video with title: "MOVIE | Official Trailer | In Cinemas Now"
        - Call get_data()
        - Verify: Cleaned title is "MOVIE" (suffix removed)

        EXPECTED BEHAVIOR:
        - Should extract before "| Official Trailer"
        - "In Cinemas Now" should be automatically filtered
        """
        pass


class TestYouTubeClientsComparison:
    """Test that both YouTube clients handle similar scenarios differently."""

    def test_rotten_tomatoes_vs_mubi_different_formats(self):
        """
        Test that clients handle their respective formats correctly.

        NEEDS:
        - RottenTomatoesClient processes: "Title Official Trailer #1 (2025)"
        - MubiClient processes: "TITLE | Official Trailer #1"
        - Both extract: "Title" / "TITLE"
        - Both skip teasers

        EXPECTED BEHAVIOR:
        - Each client uses its own _clean_title() implementation
        - Both filter by their respective patterns
        - Both inherit from YouTubeBaseClient for common logic
        """
        pass

    def test_both_clients_skip_teasers(
        self, rotten_tomatoes_client_mocked, mubi_client_mocked
    ):
        """
        Test that both clients skip teaser videos.

        NEEDS:
        - RottenTomatoesClient.get_data() with teaser
        - MubiClient.get_data() with teaser
        - Both should skip teasers in their format

        EXPECTED BEHAVIOR:
        - RottenTomatoes: "Official Teaser" → skipped
        - Mubi: "Official Teaser" → skipped
        - Both return fewer results when teasers present
        """
        pass
