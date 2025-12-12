"""
Dramatiq tasks for the movies app.

Defines async tasks and cron jobs for movie data fetching and processing.
"""

import logging

import dramatiq
from dramatiq_crontab import cron

from contrib.tmdb import TMDBClient
from contrib.youtube import MubiClient, RottenTomatoesClient

from .models import Movie

logger = logging.getLogger(__name__)


def _fetch_and_save_videos(client, source_name):
    """
    Core logic: Fetch videos from a YouTube client and save to database.

    This is a reusable helper for both RottenTomatoes and MUBI channels.

    Args:
        client: YouTube client instance (RottenTomatoesClient or MubiClient)
        source_name: Source identifier for database ('rotten_tomatoes' or 'mubi')
    """
    logger.info(f"Starting {source_name} video fetch...")

    try:
        # Fetch videos
        videos = client.get_videos()

        if not videos:
            logger.info(f"No videos found from {source_name}")
            return

        logger.info(f"Found {len(videos)} videos from {source_name}")

        # Save to database
        created_count = 0
        skipped_count = 0

        for video in videos:
            # Check if movie already exists by title
            existing_movie = Movie.objects.filter(title=video["title"]).first()

            if existing_movie:
                # Movie already exists, skip it
                logger.info(f"[SKIPPED] {video['title']} already in database")
                skipped_count += 1
                continue

            # Create new movie
            movie = Movie.objects.create(
                title=video["title"],
                original_title=video["original_title"],
                video_id=video["video_id"],
                source=source_name,
            )
            print(movie)
            created_count += 1
            logger.info(f"[NEW] {video['title']} ({video['year']})")

        logger.info(f"Task completed: {created_count} new, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"Error fetching {source_name} videos: {e}", exc_info=True)
        raise


@cron("0 0 * * *")  # Run daily at midnight UTC
@dramatiq.actor(max_retries=3)
def fetch_rotten_tomatoes_videos():
    """
    Cron Task: Fetch RottenTomatoes YouTube channel videos.

    Fetches latest videos and saves to database.
    Runs daily at midnight UTC.
    """
    client = RottenTomatoesClient()
    _fetch_and_save_videos(client, "rotten_tomatoes")


@cron("0 1 * * *")  # Run daily at 1 AM UTC (after YouTube fetch at midnight)
@dramatiq.actor(max_retries=3)
def fetch_mubi_videos():
    """
    Cron Task: Fetch MUBI YouTube channel videos.

    Fetches latest videos and saves to database.
    Runs daily at 1 AM UTC (1 hour after RottenTomatoes fetch).
    """
    client = MubiClient()
    _fetch_and_save_videos(client, "mubi")


@cron("0 2 * * *")  # Run daily at 2 AM UTC (after MUBI fetch at 1 AM)
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
                    movie.tmdb_id = tmdb_data.get("id")
                    movie.imdb_id = tmdb_data.get("imdb_id")
                    movie.overview = tmdb_data.get("overview")
                    movie.release_date = tmdb_data.get("release_date")
                    movie.poster_path = tmdb_data.get("poster_path")
                    movie.backdrop_path = tmdb_data.get("backdrop_path")
                    movie.save()

                    enriched_count += 1
                    logger.info(
                        f"[ENRICHED] {movie.title} with TMDB ID: {tmdb_data.get('id')}"
                    )
                else:
                    logger.info(f"[NOT FOUND] {movie.title} not found on TMDB")

            except Exception as e:
                logger.error(f"Error enriching {movie.title}: {e}")
                continue

        logger.info(f"Task completed: {enriched_count} movies enriched")

    except Exception as e:
        logger.error(f"Error in enrich_movies_with_tmdb: {e}", exc_info=True)
        raise
