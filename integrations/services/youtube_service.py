import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

class YouTubeService:
    CHANNEL_ID = "UCE0Wkd9Jcn2-TNo5G8bLQrA"
    BASE_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'media': 'http://search.yahoo.com/mrss/'
    }

    def __init__(self, channel_id=None):
        self.channel_id = channel_id or self.CHANNEL_ID



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
            str: The XML content, or None if fetch failed
        """
        try:
            url = self._build_rss_url()
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSS: {e}")
            return None

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
        except Exception as e:
            print(f"Error parsing RSS: {e}")
            return []

    def _extract_video_id(self, video_url):
        """
        Extract video ID from YouTube URL.

        Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        Output: dQw4w9WgXcQ
        """
        try:
            parsed_url = urlparse(video_url)
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            return video_id if video_id else ''
        except Exception as e:
            print(f"Error extracting video ID: {e}")
            return ''

    def _extract_title_and_id(self, videos):
        """
        Extract only title and video_id from parsed videos

        Input: List of video dicts with title, video_url, etc.
        Output: List of dicts with only title and video_id
        """
        processed = []
        for video in videos:
            video_id = self._extract_video_id(video['video_url'])
            processed.append({
                'title': video['title'],
                'video_id': video_id
            })
        return processed

    def get_videos(self):
        """
        Main method to fetch and parse YouTube videos.

        Returns:
            list: List of video dictionaries with title and video_id
        """
        xml_content = self._fetch_rss()
        if xml_content is None:
            return []

        videos = self._parse_rss(xml_content)
        processed_videos = self._extract_title_and_id(videos)
        return processed_videos
