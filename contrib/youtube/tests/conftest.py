"""
Shared pytest fixtures for YouTube API tests.
"""
import pytest


@pytest.fixture
def mock_rotten_tomatoes_videos():
    """Fixture: Raw video data from RottenTomatoes channel."""
    return [
        {
            'title': 'The Lord of the Rings Official Trailer #1 (2025)',
            'video_id': 'abc123',
            'description': 'Official trailer',
            'published': '20250101',
        },
        {
            'title': 'Dune Part Two Official Trailer #1 (2024)',
            'video_id': 'xyz789',
            'description': 'Official trailer',
            'published': '20240101',
        },
        {
            'title': 'Avatar Official Teaser (2025)',  # Should be skipped (teaser, not trailer)
            'video_id': 'skip123',
            'description': 'Teaser',
            'published': '20250101',
        },
    ]


@pytest.fixture
def mock_mubi_videos():
    """Fixture: Raw video data from Mubi channel."""
    return [
        {
            'title': 'DUNE | Official Trailer #1 | Coming Soon',
            'video_id': 'mubi_abc123',
            'description': 'Official trailer',
            'published': '20250101',
        },
        {
            'title': 'BLADE RUNNER 2049 | Official Trailer | In Cinemas Now',
            'video_id': 'mubi_xyz789',
            'description': 'Official trailer',
            'published': '20240101',
        },
        {
            'title': 'OPPENHEIMER | Official Teaser (2023)',  # Should be skipped (teaser)
            'video_id': 'mubi_skip123',
            'description': 'Teaser',
            'published': '20230101',
        },
    ]
