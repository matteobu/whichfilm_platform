# 15. Dramatiq Tasks: Background Job Scheduler

## What is Dramatiq?

Dramatiq is a **job queue/task scheduler** for Python. It lets you:
- Run long-running operations in the background
- Schedule tasks to run at specific times
- Process tasks asynchronously (non-blocking)

Without Dramatiq, long operations would block the web server.

## Why Do We Need It?

### Without Dramatiq (Bad)

```
User visits /movies/
   ↓
View tries to fetch YouTube videos
   ↓
Takes 30 seconds...
   ↓
User waits 30 seconds for page to load ❌
```

### With Dramatiq (Good)

```
User visits /movies/
   ↓
View returns immediately with existing data ✅
   ↓
In background: Fetch YouTube videos
   ↓
Task completes (user doesn't wait)
```

## How Dramatiq Works

```
Task Definition (Function)
         ↓
    Decorator (@dramatiq.actor)
         ↓
    Task Queue (Redis/RabbitMQ)
         ↓
    Background Worker Process
         ↓
    Task Execution
         ↓
    Result Storage
```

## Task Definition

### Basic Task

```python
import dramatiq
from django.core.mail import send_mail

@dramatiq.actor
def send_welcome_email(user_email):
    send_mail(
        'Welcome!',
        'Thanks for signing up',
        'noreply@example.com',
        [user_email]
    )
```

### Calling a Task

```python
# Enqueue immediately
send_welcome_email.send('user@example.com')

# Returns immediately (non-blocking)
```

## In This Project: Cron Tasks

The whichmovie_app uses Dramatiq for **scheduled tasks** that run at specific times.

### Decorator Breakdown

```python
@dramatiq.actor(max_retries=3)
@cron('0 0 * * *')
def fetch_rotten_tomatoes_videos():
    # Task code here
```

- **@dramatiq.actor** - Make this a Dramatiq task
- **max_retries=3** - If fails, retry up to 3 times
- **@cron()** - Schedule when to run

### Cron Schedule Syntax

```
Cron Format: minute hour day month weekday

0    0    *    *    *
│    │    │    │    │
│    │    │    │    └─ Weekday (0=Sunday, 6=Saturday)
│    │    │    └────── Month (1-12)
│    │    └─────────── Day (1-31)
│    └──────────────── Hour (0-23)
└─────────────────────  Minute (0-59)

Examples:
'0 0 * * *'       = Every day at 00:00 (midnight)
'0 1 * * *'       = Every day at 01:00
'0 2 * * *'       = Every day at 02:00
'0 */6 * * *'     = Every 6 hours
'0 0 1 * *'       = Every month on day 1 at 00:00
'0 9 * * 1-5'     = Weekdays (Mon-Fri) at 09:00
```

---

## The Three Tasks in WhichMovie

### Task 1: Fetch RottenTomatoes Videos

```python
# movies/tasks.py:70-80
@dramatiq.actor(max_retries=3)
@cron('0 0 * * *')
def fetch_rotten_tomatoes_videos():
    """
    Fetch videos from RottenTomatoes Indie channel.

    Runs: Daily at 00:00 UTC (midnight)
    Retries: Up to 3 times if fails
    Duration: ~30 seconds
    """
    client = RottenTomatoesClient()
    _fetch_and_save_videos(client, 'rotten_tomatoes')
```

**Timeline:**
```
00:00 UTC - Task starts
00:05 UTC - Task completes
01:00 UTC - Next task starts (Mubi)
```

**What it does:**
1. Create RottenTomatoesClient
2. Connect to YouTube (via yt-dlp)
3. Fetch ~20 videos from channel
4. Parse titles
5. Filter out teasers
6. Save to database

### Task 2: Fetch Mubi Videos

```python
# movies/tasks.py:83-93
@dramatiq.actor(max_retries=3)
@cron('0 1 * * *')
def fetch_mubi_videos():
    """
    Fetch videos from Mubi channel.

    Runs: Daily at 01:00 UTC
    Retries: Up to 3 times if fails
    Duration: ~30 seconds
    """
    client = MubiClient()
    _fetch_and_save_videos(client, 'mubi')
```

**Timeline:**
```
01:00 UTC - Task starts
01:05 UTC - Task completes
02:00 UTC - Next task starts (TMDB enrichment)
```

### Task 3: Enrich with TMDB

```python
# movies/tasks.py:96-152
@dramatiq.actor(max_retries=3)
@cron('0 2 * * *')
def enrich_movies_with_tmdb():
    """
    Enrich movies with TMDB metadata.

    Runs: Daily at 02:00 UTC
    Retries: Up to 3 times if fails
    Duration: ~60 seconds (depends on movie count)
    """
    unenriched = Movie.objects.filter(tmdb_id__isnull=True)

    if not unenriched.exists():
        logger.info("No unenriched movies")
        return

    client = TMDBClient()

    for movie in unenriched:
        # Search TMDB
        tmdb_data = client.search_movie(movie.title)

        if not tmdb_data:
            logger.warning(f"Not found: {movie.title}")
            continue

        # Update movie
        movie.tmdb_id = tmdb_data['id']
        movie.imdb_id = tmdb_data.get('imdb_id')
        movie.overview = tmdb_data.get('overview')
        movie.release_date = tmdb_data.get('release_date')
        movie.poster_path = tmdb_data.get('poster_path')
        movie.backdrop_path = tmdb_data.get('backdrop_path')
        movie.save()

        logger.info(f"Enriched: {movie.title}")
```

**Timeline:**
```
02:00 UTC - Task starts
02:30 UTC - Task completes
Next day 00:00 UTC - Cycle repeats
```

---

## Task Execution Environment

### Background Worker

To run tasks, you need a **worker process**:

```bash
# Terminal 1: Web server
python manage.py runserver

# Terminal 2: Task worker
dramatiq movies.tasks
```

The worker:
- Listens for new tasks
- Executes them in background
- Handles retries
- Logs results

### Queue System

```
Django App
   ├─ Web request comes in
   ├─ Enqueue task: send_email.send(...)
   └─ Return immediately to user
        ↓
   Task Queue (Redis/RabbitMQ)
        ├─ Store pending tasks
        └─ Wait for worker
             ↓
   Background Worker
        ├─ Get task from queue
        ├─ Execute task code
        ├─ Handle result/error
        └─ Remove from queue
```

## Task Lifecycle

### Success Case

```
1. SCHEDULED
   └─ Wait for cron time (00:00 UTC)

2. ENQUEUED
   └─ Add to task queue

3. EXECUTING
   ├─ Worker picks up task
   ├─ Run code
   └─ Duration: ~30 seconds

4. COMPLETED
   └─ Log: "Task completed successfully"

Next execution: Tomorrow at 00:00 UTC
```

### Failure Case

```
1. EXECUTING
   └─ Error occurs (e.g., network timeout)

2. RETRY 1
   └─ Wait 5 seconds, try again

3. RETRY 2
   └─ Wait 10 seconds, try again

4. RETRY 3
   └─ Wait 20 seconds, try again

5. FAILED
   └─ Log error, give up
   └─ Next execution: Tomorrow at 00:00 UTC
```

## Helper Function

### _fetch_and_save_videos()

Both fetch tasks use the same helper:

```python
def _fetch_and_save_videos(client, source_name):
    """
    Shared logic for fetching and saving videos.

    Args:
        client: YouTube client (RottenTomatoesClient or MubiClient)
        source_name: 'rotten_tomatoes' or 'mubi'
    """
    videos = client.get_videos()  # ← Fetch from YouTube
    created = 0
    skipped = 0

    for video in videos:
        # Check if already exists
        existing = Movie.objects.filter(title=video['title']).first()
        if existing:
            skipped += 1
            logger.info(f"[SKIPPED] {video['title']}")
            continue

        # Create new movie
        Movie.objects.create(
            title=video['title'],
            original_title=video['original_title'],
            video_id=video['video_id'],
            source=source_name
        )
        created += 1
        logger.info(f"[CREATED] {video['title']}")

    logger.info(f"Fetch {source_name}: Created {created}, Skipped {skipped}")
```

## Monitoring Tasks

### View Logs

Tasks log what they do:

```
[2025-11-21 00:00:00] Task: fetch_rotten_tomatoes_videos started
[2025-11-21 00:00:15] [CREATED] The Lord of the Rings
[2025-11-21 00:00:20] [SKIPPED] Inception (already exists)
[2025-11-21 00:00:30] Fetch rotten_tomatoes: Created 2, Skipped 1
[2025-11-21 00:00:31] Task completed
```

### Task Result

After execution:
```python
# Check last run
movie_count = Movie.objects.filter(source='rotten_tomatoes').count()
# Result: 42 movies from RottenTomatoes
```

## Task Order Matters

```
00:00 - RottenTomatoes fetch
   ↓
01:00 - Mubi fetch
   ↓
02:00 - TMDB enrichment
```

Why this order?

1. **RottenTomatoes first** - Most reliable, runs first
2. **Mubi second** - Don't overlap with RottenTomatoes
3. **TMDB enrichment last** - Let both fetches complete first

## Task Reliability Features

### 1. Automatic Retries

```python
@dramatiq.actor(max_retries=3)
```
If task fails, retry up to 3 times automatically.

### 2. Logging

```python
logger.info(f"[CREATED] {movie.title}")
logger.warning(f"Not found: {movie.title}")
logger.error(f"Error: {error_message}")
```
Track what tasks did.

### 3. Database Transactions

```python
Movie.objects.create(...)  # ← Atomic operation
```
Create movie atomically (all or nothing).

### 4. Duplicate Detection

```python
existing = Movie.objects.filter(title=video['title']).first()
if existing:
    skip()  # ← Don't create duplicate
```
Check before creating.

## Dramatiq Configuration

In settings.py:

```python
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://localhost:6379",
    }
}
```

- **Broker** - Message queue (Redis/RabbitMQ)
- **URL** - Location of Redis
- **Default retry** - 3 times
- **Default timeout** - 600 seconds

## Comparing Approaches

| Aspect | Without Task Scheduler | With Dramatiq |
|--------|----------------------|---------------|
| Fetching videos | Manual (on demand) | Automatic (daily) |
| Data freshness | Depends on user | Always fresh (daily) |
| User experience | Slow on first fetch | Fast (cached data) |
| Scalability | Doesn't scale | Scales to many tasks |
| Reliability | Manual retries needed | Auto-retry built-in |
| Monitoring | Hard to track | Easy to log/monitor |

---

Next: [Testing](./16_testing.md)
