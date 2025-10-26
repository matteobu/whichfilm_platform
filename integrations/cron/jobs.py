import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whichfilm.settings')
django.setup()

from integrations.clients import YouTubeAPIClient
from integrations.models import SourceFilmTitle


def fetch_youtube_videos():
    """
    Fetch latest YouTube videos and save to database.
    This job is called by a cron job every 12 hours.
    """
    print("=" * 50)
    print("Starting fetch_youtube_videos job...")
    print("=" * 50)

    try:
        # Fetch videos from YouTube
        client = YouTubeAPIClient()
        videos = client.get_videos()

        if not videos:
            print("No videos found")
            return

        print(f"Found {len(videos)} videos")

        # Save to database
        created_count = 0
        updated_count = 0

        for video in videos:
            obj, created = SourceFilmTitle.objects.update_or_create(
                video_id=video['video_id'],
                defaults={
                    'title': video['title'],
                    'year': video['year'],
                    'original_title': video['original_title'],
                    'source': 'youtube'
                }
            )

            if created:
                created_count += 1
                print(f"[NEW] {video['title']} ({video['year']})")
            else:
                updated_count += 1
                print(f"[UPDATED] {video['title']} ({video['year']})")

        print("=" * 50)
        print(f"Job completed: {created_count} new, {updated_count} updated")
        print("=" * 50)

    except Exception as e:
        print(f"Error in fetch_youtube_videos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)