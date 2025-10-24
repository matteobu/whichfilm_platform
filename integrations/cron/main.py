#!/usr/bin/env python
"""
Main entry point for cron jobs.
Usage: python main.py <job_name>
Example: python main.py fetch_youtube_videos
"""

import sys
from jobs import fetch_youtube_videos

# Available jobs
JOBS = {
    'fetch_youtube_videos': fetch_youtube_videos,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <job_name>")
        print(f"Available jobs: {', '.join(JOBS.keys())}")
        sys.exit(1)

    job_name = sys.argv[1]

    if job_name not in JOBS:
        print(f"Job '{job_name}' not found")
        print(f"Available jobs: {', '.join(JOBS.keys())}")
        sys.exit(1)

    # Execute the job
    job = JOBS[job_name]
    job()


if __name__ == '__main__':
    main()
