"""
Dramatiq tasks for the festivals app.

Defines async tasks and cron jobs for festival data fetching and processing.
"""

import dramatiq
import logging

logger = logging.getLogger(__name__)


# TODO: Implement festival data fetching tasks
# Example placeholder for future festival integration:
#
# @dramatiq.actor(max_retries=3)
# def fetch_festival_movies():
#     """
#     Task: Fetch festival movie data and save to database.
#
#     This will integrate with FestivalClient from contrib/festivals/
#     """
#     pass
