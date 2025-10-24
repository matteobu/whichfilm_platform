from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from integrations.cron.jobs import fetch_youtube_videos

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Start the background scheduler with all scheduled tasks.
    Call this once when Django starts.
    """
    if not scheduler.running:
        # Schedule the YouTube fetch task to run at 00:00, 08:00, and 16:00 every day
        scheduler.add_job(
            fetch_youtube_videos,
            CronTrigger(hour='0,8,16', minute='0'),
            id='fetch_youtube_videos',
            name='Fetch YouTube Videos',
            replace_existing=True
        )
        scheduler.start()
        print("Scheduler started successfully!")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped!")
