"""YouTube API client for fetching video information from multiple channels."""

import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import logging

from contrib.base import BaseClient, ValidationError, NetworkError

logger = logging.getLogger(__name__)


class YouTubeBaseClient(BaseClient):
    """
    Base class for YouTube channel clients.

    Provides common functionality for fetching and parsing RSS feeds from YouTube channels.
    Subclasses override _clean_title() to handle channel-specific title formats.
    """

    BASE_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
    CHANNEL_ID = None  # Override in subclasses
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'media': 'http://search.yahoo.com/mrss/'
    }

    def __init__(self):
        """Initialize YouTube base client."""
        if not self.CHANNEL_ID:
            raise ValidationError("CHANNEL_ID must be defined in subclass")
        self.channel_id = self.CHANNEL_ID
        super().__init__()

    def _validate_config(self):
        """Validate that the client is properly configured."""
        if not self.channel_id:
            raise ValidationError("YouTube channel_id is required")

    def _build_rss_url(self):
        """
        Build the YouTube RSS feed URL for the channel.

        Returns:
            str: The full RSS feed URL
        """
        return self.BASE_RSS_URL.format(self.channel_id)

    def _fetch_rss(self):
        """
        Fetch the RSS feed from YouTube.

        Returns:
            str: The XML content

        Raises:
            NetworkError: If the request fails
        """
        try:
            url = self._build_rss_url()
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Error fetching YouTube RSS: {e}") from e

    def _parse_rss(self, xml_content):
        """
        Parse the RSS feed XML and extract video data.

        Args:
            xml_content (str): The raw XML content from YouTube

        Returns:
            list: List of dictionaries with video data
        """
        try:
            root = ET.fromstring(xml_content)
            namespaces = self.NAMESPACES
            entries = root.findall('atom:entry', namespaces)

            videos = []
            for entry in entries:
                title_elem = entry.find('atom:title', namespaces)
                description_elem = entry.find('atom:summary', namespaces)
                published_elem = entry.find('atom:published', namespaces)
                link_elem = entry.find('atom:link', namespaces)
                thumbnail_elem = entry.find('media:thumbnail', namespaces)

                video = {
                    'title': title_elem.text if title_elem is not None else '',
                    'description': description_elem.text if description_elem is not None else '',
                    'published': published_elem.text if published_elem is not None else '',
                    'video_url': link_elem.get('href') if link_elem is not None else '',
                    'thumbnail': thumbnail_elem.get('url') if thumbnail_elem is not None else '',
                }
                videos.append(video)
            return videos
        except ET.ParseError as e:
            raise ValidationError(f"Error parsing YouTube RSS XML: {e}") from e

    def _extract_video_id(self, video_url):
        """
        Extract video ID from YouTube URL.

        Args:
            video_url (str): YouTube video URL

        Returns:
            str: Video ID, or empty string if extraction fails
        """
        try:
            parsed_url = urlparse(video_url)
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            return video_id if video_id else ''
        except Exception as e:
            logger.error(f"Error extracting video ID: {e}")
            return ''

    def _extract_year(self, title):
        """
        Extract year from title (format: any text with (YYYY)).

        Args:
            title (str): Video title

        Returns:
            int or None: Year if found, None otherwise
        """
        match = re.search(r'\((\d{4})\)', title)
        if match:
            return int(match.group(1))
        return None

    def _clean_title(self, title):
        """
        Clean and extract movie title from video title.

        This method should be overridden by subclasses to handle
        channel-specific title formats.

        Args:
            title (str): Raw video title

        Returns:
            str or None: Cleaned movie title, or None if invalid format
        """
        raise NotImplementedError("Subclasses must implement _clean_title()")

    def _extract_title_and_id(self, videos):
        """
        Extract title, year, and video_id from parsed videos.

        Args:
            videos (list): List of video dicts with title, video_url, etc.

        Returns:
            list: List of dicts with cleaned title, year, original_title, and video_id
        """
        processed = []
        for video in videos:
            original_title = video['title']

            # Clean title using channel-specific logic
            cleaned_title = self._clean_title(original_title)

            # Skip if title doesn't match channel format
            if cleaned_title is None:
                continue

            # Extract year
            year = self._extract_year(original_title)

            # Extract video ID
            video_id = self._extract_video_id(video['video_url'])

            processed.append({
                'title': cleaned_title,
                'year': year,
                'original_title': original_title,
                'video_id': video_id
            })
        return processed

    def get_data(self, **kwargs):
        """
        Main method to fetch and parse YouTube videos.

        Returns:
            list: List of video dictionaries with title and video_id

        Raises:
            NetworkError: If fetching fails
            ValidationError: If parsing fails
        """
        xml_content = self._fetch_rss()
        videos = self._parse_rss(xml_content)
        processed_videos = self._extract_title_and_id(videos)
        return processed_videos


class RottenTomatoesClient(YouTubeBaseClient):
    """
    RottenTomatoes INDIE channel client.

    Handles title format: "Movie Title Trailer #1 (2025)"
    Only processes official trailers (Trailer #), skips teasers.
    """

    CHANNEL_ID = "UCLyYEq4ODlw3OD9qhGqwimw"

    def _clean_title(self, title):
        """
        Extract movie title from RottenTomatoes trailer format.

        Format: "Movie Title Trailer #1 (2025)" → "Movie Title"
        Skips teaser trailers (no Trailer # pattern).

        Args:
            title (str): Video title

        Returns:
            str or None: Cleaned title, or None if not official trailer
        """
        # Only process if it has "Trailer #" (official trailers, not teasers)
        if 'Trailer #' not in title:
            return None

        # Extract everything before "Trailer #"
        match = re.match(r'^(.+?)\s+Trailer\s+#', title)

        if match:
            cleaned = match.group(1).strip()
            return cleaned if cleaned else None

        return None

    def get_videos(self):
        """Fetch videos from RottenTomatoes channel."""
        return self.get_data()


class MubiClient(YouTubeBaseClient):
    """
    Mubi channel client.

    Handles Mubi-specific title format.
    Override _clean_title() with Mubi-specific parsing logic.
    """

    CHANNEL_ID = "UUEuIk8O5Cyzl8J_ylPFzA"

    def _clean_title(self, title):
        """
        Extract movie title from Mubi title format.

        Format: "MOVIE TITLE | Official Trailer #1 | ..." → "MOVIE TITLE"
        Skips teasers and "Coming Soon" announcements.

        Args:
            title (str): Video title

        Returns:
            str or None: Cleaned title, or None if invalid format
        """
        # Exclude teasers and "Coming Soon"
        if 'Official Teaser' in title or 'Coming Soon' in title:
            return None

        # Only process if it has "Official Trailer"
        if 'Official Trailer' not in title:
            return None

        # Extract everything before "Official Trailer" (remove pipes and whitespace)
        match = re.match(r'^(.+?)\s*\|\s*Official Trailer', title)

        if match:
            cleaned = match.group(1).strip()
            return cleaned if cleaned else None

        return None

    def get_videos(self):
        """Fetch videos from Mubi channel."""
        return self.get_data()


# Legacy alias for backward compatibility
class YouTubeClient(RottenTomatoesClient):
    """
    Legacy alias for RottenTomatoesClient.

    Use RottenTomatoesClient or MubiClient directly for clarity.
    """
    pass
