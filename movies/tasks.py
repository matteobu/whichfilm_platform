"""
Dramatiq tasks for the movies app.

Defines async tasks and cron jobs for movie data fetching and processing.
"""

import dramatiq
from dramatiq_crontab import cron
from contrib.youtube import YouTubeClient
from contrib.tmdb import TMDBClient
from .models import Movie
import logging

logger = logging.getLogger(__name__)


@cron('0 0 * * *')  # Run daily at midnight UTC
@dramatiq.actor(max_retries=3)
def fetch_youtube_videos():
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


@cron('0 2 * * *')  # Run daily at 2 AM UTC (after YouTube fetch at midnight)
@dramatiq.actor(max_retries=3)
def enrich_movies_with_tmdb():
    """
    Cron Task: Enrich movies with TMDB data.

    Fetches movies without tmdb_id from TMDB using their titles,
    and updates them with TMDB metadata.

    Runs daily at 2 AM UTC (2 hours after YouTube fetch).
    """
    logger.info("Starting TMDB enrichment task...")

    try:
        # Get all movies without tmdb_id
        movies_to_enrich = Movie.objects.filter(tmdb_id__isnull=True)

        if not movies_to_enrich.exists():
            logger.info("No movies to enrich")
            return

        logger.info(f"Found {movies_to_enrich.count()} movies to enrich")

        # Initialize TMDB client
        client = TMDBClient()

        enriched_count = 0

        for movie in movies_to_enrich:
            try:
                # Search TMDB for this movie
                tmdb_data = client.search_movie(movie.title)

                if tmdb_data:
                    # Update movie with TMDB data
                    movie.tmdb_id = tmdb_data.get('id')
                    movie.imdb_id = tmdb_data.get('imdb_id')
                    movie.overview = tmdb_data.get('overview')
                    movie.release_date = tmdb_data.get('release_date')
                    movie.poster_path = tmdb_data.get('poster_path')
                    movie.save()

                    enriched_count += 1
                    logger.info(f"[ENRICHED] {movie.title} with TMDB ID: {tmdb_data.get('id')}")
                else:
                    logger.info(f"[NOT FOUND] {movie.title} not found on TMDB")

            except Exception as e:
                logger.error(f"Error enriching {movie.title}: {e}")
                continue

        logger.info(f"Task completed: {enriched_count} movies enriched")

    except Exception as e:
        logger.error(f"Error in enrich_movies_with_tmdb: {e}", exc_info=True)
        raise