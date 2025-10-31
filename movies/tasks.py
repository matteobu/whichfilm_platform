"""
Dramatiq tasks for the movies app.

Defines async tasks and cron jobs for movie data fetching and processing.
"""

import dramatiq
from dramatiq_crontab import cron
from contrib.youtube import YouTubeClient
from .models import Movie
import logging

logger = logging.getLogger(__name__)


def _fetch_and_save_youtube_videos():
    """
    Core logic: Fetch YouTube videos and save to database.

    This is the actual implementation that both:
    - The Dramatiq cron job calls
    - Manual CLI calls use

    Can be called from:
    1. Cron job (automatic)
    2. Shell: from movies.tasks import _fetch_and_save_youtube_videos; _fetch_and_save_youtube_videos()
    """
    logger.info("Starting YouTube video fetch...")

    try:
        # Fetch videos from YouTube
        client = YouTubeClient()
        videos = client.get_videos()

        if not videos:
            logger.info("No videos found from YouTube")
            return

        logger.info(f"Found {len(videos)} videos from YouTube")

        # Save to database
        created_count = 0
        updated_count = 0

        for video in videos:
            movie, created = Movie.objects.update_or_create(
                video_id=video['video_id'],
                defaults={
                    'title': video['title'],
                    'original_title': video['original_title'],
                    'source': 'youtube_title'
                }
            )

            if created:
                created_count += 1
                logger.info(f"[NEW] {video['title']} ({video['year']})")
            else:
                updated_count += 1
                logger.info(f"[UPDATED] {video['title']} ({video['year']})")

        logger.info(f"Task completed: {created_count} new, {updated_count} updated")

    except Exception as e:
        logger.error(f"Error fetching YouTube videos: {e}", exc_info=True)
        raise


@cron('0 0 * * *')  # Run daily at midnight UTC
@dramatiq.actor(max_retries=3)
def fetch_youtube_videos():
    """
    Dramatiq Cron Task: Fetch latest YouTube videos and save to Movie database.

    Runs automatically every day at midnight (UTC).
    Can also be triggered manually via:
    - Shell: fetch_youtube_videos.send()
    - Or call _fetch_and_save_youtube_videos() directly
    """
    _fetch_and_save_youtube_videos()
