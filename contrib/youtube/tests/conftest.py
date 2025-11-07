"""
Shared pytest fixtures for YouTube API tests.
"""
import pytest
from unittest.mock import MagicMock
from contrib.youtube.api import RottenTomatoesClient, MubiClient


# ============================================================================
# Mock yt-dlp Response Data (format that YoutubeDL.extract_info returns)
# ============================================================================

@pytest.fixture
def mock_yt_dlp_rotten_tomatoes_response():
    """Fixture: Mock yt-dlp response for RottenTomatoes channel."""
    return {
        'entries': [
            {
                'title': 'The Lord of the Rings Official Trailer #1 (2025)',
                'id': 'abc123',
                'description': 'Official trailer',
                'upload_date': '20250101',
                'url': 'https://youtube.com/watch?v=abc123',
                'thumbnail': 'https://i.ytimg.com/vi/abc123/default.jpg',
            },
            {
                'title': 'Dune Part Two Official Trailer #1 (2024)',
                'id': 'xyz789',
                'description': 'Sci-fi epic',
                'upload_date': '20240615',
                'url': 'https://youtube.com/watch?v=xyz789',
                'thumbnail': 'https://i.ytimg.com/vi/xyz789/default.jpg',
            },
            {
                'title': 'Avatar Official Teaser (2025)',
                'id': 'skip123',
                'description': 'Teaser (should be skipped)',
                'upload_date': '20250101',
                'url': 'https://youtube.com/watch?v=skip123',
                'thumbnail': 'https://i.ytimg.com/vi/skip123/default.jpg',
            },
        ]
    }


@pytest.fixture
def mock_yt_dlp_mubi_response():
    """Fixture: Mock yt-dlp response for Mubi channel."""
    return {
        'entries': [
            {
                'title': 'DUNE | Official Trailer #1',
                'id': 'mubi_abc123',
                'description': 'Sci-fi epic',
                'upload_date': '20250101',
                'url': 'https://youtube.com/watch?v=mubi_abc123',
                'thumbnail': 'https://i.ytimg.com/vi/mubi_abc123/default.jpg',
            },
            {
                'title': 'BLADE RUNNER 2049 | Official Trailer | In Cinemas Now',
                'id': 'mubi_xyz789',
                'description': 'Sci-fi masterpiece',
                'upload_date': '20240601',
                'url': 'https://youtube.com/watch?v=mubi_xyz789',
                'thumbnail': 'https://i.ytimg.com/vi/mubi_xyz789/default.jpg',
            },
            {
                'title': 'OPPENHEIMER | Official Teaser (2023)',
                'id': 'mubi_skip123',
                'description': 'Teaser (should be skipped)',
                'upload_date': '20230615',
                'url': 'https://youtube.com/watch?v=mubi_skip123',
                'thumbnail': 'https://i.ytimg.com/vi/mubi_skip123/default.jpg',
            },
        ]
    }


@pytest.fixture
def mock_yt_dlp_empty_response():
    """Fixture: Empty yt-dlp response (no videos)."""
    return {
        'entries': []
    }


# ============================================================================
# Mocked YoutubeDL Instance Fixtures
# ============================================================================

@pytest.fixture
def mock_yt_dlp_instance(mock_yt_dlp_rotten_tomatoes_response):
    """Fixture: Mocked YoutubeDL instance with RottenTomatoes response."""
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_yt_dlp_rotten_tomatoes_response
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.__exit__.return_value = None
    return mock_instance


@pytest.fixture
def mock_yt_dlp_instance_mubi(mock_yt_dlp_mubi_response):
    """Fixture: Mocked YoutubeDL instance with Mubi response."""
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_yt_dlp_mubi_response
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.__exit__.return_value = None
    return mock_instance


# ============================================================================
# Client Fixtures with Mocked YoutubeDL
# ============================================================================

@pytest.fixture
def rotten_tomatoes_client_mocked(monkeypatch, mock_yt_dlp_instance):
    """Fixture: RottenTomatoesClient with mocked yt-dlp."""
    monkeypatch.setattr(
        'contrib.youtube.api.YoutubeDL',
        lambda *args, **kwargs: mock_yt_dlp_instance
    )
    return RottenTomatoesClient()


@pytest.fixture
def mubi_client_mocked(monkeypatch, mock_yt_dlp_instance_mubi):
    """Fixture: MubiClient with mocked yt-dlp."""
    monkeypatch.setattr(
        'contrib.youtube.api.YoutubeDL',
        lambda *args, **kwargs: mock_yt_dlp_instance_mubi
    )
    return MubiClient()
