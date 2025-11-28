# Movies App - Code Implementation Guide

A comprehensive guide explaining what's happening **inside each file** of the movies Django app.

## Overview

The `movies` app is the core feature of the WhichMovie project. It:
1. Defines the Movie database model
2. Provides views for displaying movies
3. Runs background tasks to fetch and enrich movie data
4. Routes URLs to the appropriate views
5. Provides Django admin interface for movie management

---

## `models.py` - Database Model Definition

**Purpose:** Define the Movie database model that represents a movie record.

### Movie Model

```python
class Movie(models.Model):
    # Core identifiers
    title = models.CharField(max_length=255)                    # Required: cleaned/normalized title
    original_title = models.CharField(max_length=255, blank=True, null=True)  # Raw YouTube title

    # External IDs for deduplication and enrichment
    tmdb_id = models.IntegerField(blank=True, null=True, unique=True)         # TMDB ID (unique)
    imdb_id = models.CharField(max_length=20, blank=True, null=True, unique=True)  # IMDb ID (unique)

    # Source tracking
    source = models.CharField(max_length=50)                    # 'rotten_tomatoes' or 'mubi'
    video_id = models.CharField(max_length=50, blank=True, null=True)  # YouTube video ID

    # TMDB enrichment fields (populated by enrich_movies_with_tmdb task)
    overview = models.TextField(blank=True, null=True)          # Plot summary from TMDB
    release_date = models.DateField(blank=True, null=True)      # Release date from TMDB
    poster_path = models.CharField(max_length=255, blank=True, null=True)     # Poster URL
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)   # Backdrop URL

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)        # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)            # Auto-updated on save
```

### Key Design Decisions

1. **Dual Title Fields**
   - `title`: Cleaned/normalized title used for display and searching
   - `original_title`: Raw YouTube title as source, for debugging/tracing

2. **Unique Constraints**
   - `tmdb_id` and `imdb_id` are unique to prevent duplicate enrichment
   - `title` is NOT unique (same movie can be from different sources with slight variations)

3. **Enrichment Pattern**
   - Videos start with `tmdb_id=NULL` when created by fetch tasks
   - `enrich_movies_with_tmdb()` task populates TMDB fields later
   - This allows fetching to be fast (no TMDB lookups) and enrichment to be parallelizable

4. **Timestamps**
   - `auto_now_add=True` on `created_at` - set once at creation
   - `auto_now=True` on `updated_at` - updated on every save

### Database Schema

```
movies_movie table:
├── id (PRIMARY KEY)
├── title (VARCHAR 255, NOT NULL)
├── original_title (VARCHAR 255, NULLABLE)
├── tmdb_id (INT, UNIQUE, NULLABLE)
├── imdb_id (VARCHAR 20, UNIQUE, NULLABLE)
├── source (VARCHAR 50, NOT NULL)
├── video_id (VARCHAR 50, NULLABLE)
├── overview (TEXT, NULLABLE)
├── release_date (DATE, NULLABLE)
├── poster_path (VARCHAR 255, NULLABLE)
├── backdrop_path (VARCHAR 255, NULLABLE)
├── created_at (TIMESTAMP, NOT NULL)
└── updated_at (TIMESTAMP, NOT NULL)
```

---

## `views.py` - HTTP Request Handlers

**Purpose:** Handle HTTP requests and return rendered HTML responses.

### `movie_list(request)` - Display All Movies

```python
def movie_list(request):
    """Display list of all movies with TMDB enrichment data."""
    # Get all movies ordered by creation date (newest first)
    movies = Movie.objects.all().order_by('-created_at')

    context = {
        'movies': movies,
        'total_movies': movies.count(),
        'enriched_movies': movies.filter(tmdb_id__isnull=False).count(),
    }

    return render(request, "movies/movie_list.html", context)
```

**What It Does:**

1. **Query all movies**: `Movie.objects.all()` - Fetches all movie records
2. **Order by date**: `.order_by('-created_at')` - Newest movies first (descending order)
3. **Count total**: `movies.count()` - Total number of movies in database
4. **Count enriched**: `movies.filter(tmdb_id__isnull=False).count()` - Movies with TMDB data
5. **Render template**: `render(request, "movies/movie_list.html", context)` - Passes data to HTML template

**Performance Notes:**
- The two `.count()` calls are database queries (not Python operations)
- This creates 3 SQL queries (1 for movies, 2 for counts)
- Could be optimized using `annotate()` for large datasets

**Template Context:**
```python
context = {
    'movies': <QuerySet of Movie objects>,
    'total_movies': <integer>,
    'enriched_movies': <integer>
}
```

**URL Pattern:** `/movies/` (mapped in `urls.py`)

**Response:** HTML page rendered from `templates/movies/movie_list.html`

---

## `tasks.py` - Background Tasks for Data Processing

**Purpose:** Define scheduled background tasks that run on a cron schedule using Dramatiq.

### Task Architecture

The file uses:
- **Dramatiq**: Async task queue for distributed task processing
- **dramatiq_crontab**: Cron scheduling for periodic tasks
- **Decorators**: `@cron()` and `@dramatiq.actor()` for task configuration

### `_fetch_and_save_videos(client, source_name)` - Core Fetch Logic

**Purpose:** Shared helper function used by both RottenTomatoes and MUBI fetch tasks.

```python
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
        # Step 1: Fetch videos from YouTube
        videos = client.get_videos()  # Returns list of video dicts with format:
        # {
        #     'title': str,           # Cleaned movie title
        #     'original_title': str,  # Raw YouTube title
        #     'video_id': str,        # YouTube video ID
        #     'year': int             # Extracted year (not used in save)
        # }

        if not videos:
            logger.info(f"No videos found from {source_name}")
            return

        logger.info(f"Found {len(videos)} videos from {source_name}")

        # Step 2: Process and save videos
        created_count = 0
        skipped_count = 0

        for video in videos:
            # Check if movie already exists by title (duplicate prevention)
            existing_movie = Movie.objects.filter(title=video['title']).first()

            if existing_movie:
                logger.info(f"[SKIPPED] {video['title']} already in database")
                skipped_count += 1
                continue  # Skip to next video

            # Create new movie record
            movie = Movie.objects.create(
                title=video['title'],
                original_title=video['original_title'],
                video_id=video['video_id'],
                source=source_name
                # Note: tmdb_id is NULL (not enriched yet)
            )
            created_count += 1
            logger.info(f"[NEW] {video['title']} ({video['year']})")

        logger.info(f"Task completed: {created_count} new, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"Error fetching {source_name} videos: {e}", exc_info=True)
        raise  # Re-raise to trigger Dramatiq retry
```

**Key Features:**

1. **Duplicate Prevention**
   - Checks if title already exists: `Movie.objects.filter(title=video['title']).first()`
   - If exists: skip and increment `skipped_count`
   - If new: create Movie record

2. **Error Handling**
   - Try/except wraps entire function
   - `exc_info=True` logs full stack trace for debugging
   - `raise` re-raises exception (triggers Dramatiq retry)

3. **Logging**
   - Info logs for progress tracking
   - Includes creation count and skip count for monitoring
   - Individual [NEW] and [SKIPPED] logs for each video

### `fetch_rotten_tomatoes_videos()` - Fetch RottenTomatoes Videos

```python
@cron('0 0 * * *')  # Run daily at midnight UTC (00:00)
@dramatiq.actor(max_retries=3)  # Retry up to 3 times if it fails
def fetch_rotten_tomatoes_videos():
    """
    Cron Task: Fetch RottenTomatoes YouTube channel videos.

    Runs daily at midnight UTC.
    """
    client = RottenTomatoesClient()  # Create client for RottenTomatoes channel
    _fetch_and_save_videos(client, 'rotten_tomatoes')  # Fetch and save
```

**Schedule:** Daily at 00:00 UTC (midnight)

**What It Does:**
1. Creates a `RottenTomatoesClient` instance
2. Calls `_fetch_and_save_videos()` with the client and source name
3. The helper function handles all the fetching and saving logic

**Retry Logic:** If task fails, Dramatiq will retry up to 3 times with exponential backoff

### `fetch_mubi_videos()` - Fetch MUBI Videos

```python
@cron('0 1 * * *')  # Run daily at 1 AM UTC (01:00)
@dramatiq.actor(max_retries=3)
def fetch_mubi_videos():
    """
    Cron Task: Fetch MUBI YouTube channel videos.

    Runs daily at 1 AM UTC (1 hour after RottenTomatoes fetch).
    """
    client = MubiClient()
    _fetch_and_save_videos(client, 'mubi')
```

**Schedule:** Daily at 01:00 UTC (1 hour after RottenTomatoes)

**Why the 1-hour delay?** Stagger the tasks to:
- Avoid simultaneous YouTube API calls
- Distribute server load
- Make logs easier to read

### `enrich_movies_with_tmdb()` - Add TMDB Metadata

```python
@cron('0 2 * * *')  # Run daily at 2 AM UTC (02:00)
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
        # Step 1: Find unenriched movies
        movies_to_enrich = Movie.objects.filter(tmdb_id__isnull=True)
        # This finds all movies where tmdb_id IS NULL

        if not movies_to_enrich.exists():
            logger.info("No movies to enrich")
            return

        logger.info(f"Found {movies_to_enrich.count()} movies to enrich")

        # Step 2: Initialize TMDB client
        client = TMDBClient()

        enriched_count = 0

        # Step 3: Process each unenriched movie
        for movie in movies_to_enrich:
            try:
                # Search TMDB by movie title
                tmdb_data = client.search_movie(movie.title)
                # Returns dict with format:
                # {
                #     'id': int,              # TMDB ID
                #     'imdb_id': str,         # IMDb ID
                #     'overview': str,        # Plot summary
                #     'release_date': date,   # Release date
                #     'poster_path': str,     # Poster image URL
                #     'backdrop_path': str    # Backdrop image URL
                # } or None if not found

                if tmdb_data:
                    # Update movie with TMDB data
                    movie.tmdb_id = tmdb_data.get('id')
                    movie.imdb_id = tmdb_data.get('imdb_id')
                    movie.overview = tmdb_data.get('overview')
                    movie.release_date = tmdb_data.get('release_date')
                    movie.poster_path = tmdb_data.get('poster_path')
                    movie.backdrop_path = tmdb_data.get('backdrop_path')
                    movie.save()  # Save to database

                    enriched_count += 1
                    logger.info(f"[ENRICHED] {movie.title} with TMDB ID: {tmdb_data.get('id')}")
                else:
                    # TMDB didn't find this movie
                    logger.info(f"[NOT FOUND] {movie.title} not found on TMDB")

            except Exception as e:
                # Log error for individual movie but continue to next movie
                logger.error(f"Error enriching {movie.title}: {e}")
                continue

        logger.info(f"Task completed: {enriched_count} movies enriched")

    except Exception as e:
        logger.error(f"Error in enrich_movies_with_tmdb: {e}", exc_info=True)
        raise  # Trigger retry
```

**Schedule:** Daily at 02:00 UTC (2 hours after RottenTomatoes, 1 hour after MUBI)

**What It Does:**

1. **Find unenriched movies**: `Movie.objects.filter(tmdb_id__isnull=True)`
   - Finds all movies where `tmdb_id` column is NULL
   - These are movies created by fetch tasks but not yet enriched

2. **For each movie**:
   - Search TMDB using movie title: `client.search_movie(movie.title)`
   - If found: Update movie with TMDB data and save
   - If not found: Log and continue to next movie

3. **Error Handling**:
   - Inner try/except for individual movie enrichment (don't fail whole task)
   - Outer try/except for task-level errors (triggers retry)

**TMDB Fields Populated:**
- `tmdb_id` - TMDB database ID
- `imdb_id` - IMDb ID (useful for cross-linking)
- `overview` - Plot summary for display
- `release_date` - Year/date info for display
- `poster_path` - Movie poster image URL
- `backdrop_path` - Background image URL

**Performance Notes:**
- Fetches ALL unenriched movies in memory
- Makes a TMDB API call for each movie (could be slow for large datasets)
- Per-movie error handling prevents one bad movie from breaking the whole task

---

## `urls.py` - URL Routing

**Purpose:** Map URL patterns to view functions.

```python
from django.urls import path
from .views import movie_list

urlpatterns = [
    path('', movie_list, name='movie_list'),
]
```

**URL Mapping:**

| URL | View Function | Name | Purpose |
|-----|---------------|------|---------|
| `/movies/` | `movie_list` | `movie_list` | Display all movies |

**How It Works:**

1. User visits URL: `http://localhost:8000/movies/`
2. Django's URL router matches the empty path `''` (relative to parent URL)
3. Calls `movie_list(request)` function
4. View returns HTML response

**Integration with Project URLs:**

In `whichmovie/urls.py`:
```python
urlpatterns = [
    path('', include('movies.urls')),  # Include movies app URLs with no prefix
    # This makes the movie_list available at /movies/
]
```

**Named URLs (Template Usage):**

In templates, you can reference the URL by name:
```html
<a href="{% url 'movie_list' %}">View All Movies</a>
<!-- Renders as: <a href="/movies/">View All Movies</a> -->
```

---

## `admin.py` - Django Admin Interface

**Purpose:** Register Movie model with Django admin and customize the display.

```python
from django.contrib import admin
from .models import Movie

@admin.register(Movie)  # Register Movie model with Django admin
class MovieAdmin(admin.ModelAdmin):
    # What columns to display in the list view
    list_display = ('title', 'source', 'tmdb_id', 'imdb_id', 'video_id', 'created_at')

    # What fields to filter by in the sidebar
    list_filter = ('source', 'created_at')

    # What fields to search by
    search_fields = ('title', 'original_title', 'tmdb_id', 'imdb_id')

    # Fields that cannot be edited (auto-set by Django)
    readonly_fields = ('created_at', 'updated_at')
```

**Features Provided:**

1. **List Display**
   - Shows `title`, `source`, `tmdb_id`, `imdb_id`, `video_id`, `created_at`
   - Admins can click on any field to sort
   - Truncates long text fields for readability

2. **Filters**
   - Filter by `source` (rotten_tomatoes, mubi) in sidebar
   - Filter by `created_at` (today, past 7 days, past month, etc.)
   - Helps admins find movies quickly

3. **Search**
   - Search by title, original_title, tmdb_id, or imdb_id
   - Case-insensitive search across these fields
   - Useful for finding specific movies

4. **Readonly Fields**
   - `created_at` and `updated_at` cannot be edited
   - Django sets these automatically on create/update

**Admin Access:**

1. Go to `http://localhost:8000/admin/`
2. Login with admin account
3. Click "Movies" section
4. View, edit, create, or delete Movie records

---

## `apps.py` - App Configuration

**Purpose:** Configure the Django app.

```python
from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Use 64-bit integers for auto IDs
    name = "movies"  # App name as used in INSTALLED_APPS
```

**Configuration Details:**

1. **`default_auto_field`**:
   - Specifies the field type for auto-generated primary keys
   - `BigAutoField` uses 64-bit integers (supports up to 9 trillion records)
   - Alternative: `AutoField` uses 32-bit integers (supports up to 2 billion records)

2. **`name`**:
   - The Python module name of the app
   - Must match the folder name: `movies`

**Usage:**

In `whichmovie/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'movies.apps.MoviesConfig',  # Register this app
    # ...
]
```

---

## Task Execution Timeline

A complete daily execution flow:

```
00:00 UTC → fetch_rotten_tomatoes_videos() runs
           ├─ Creates RottenTomatoesClient
           ├─ Calls _fetch_and_save_videos()
           ├─ Fetches videos from RottenTomatoes YouTube
           ├─ Saves movies to database with tmdb_id=NULL
           └─ Logs: "5 new, 2 skipped" (example)

01:00 UTC → fetch_mubi_videos() runs
           ├─ Creates MubiClient
           ├─ Calls _fetch_and_save_videos()
           ├─ Fetches videos from MUBI YouTube
           ├─ Saves movies to database with tmdb_id=NULL
           └─ Logs: "3 new, 1 skipped" (example)

02:00 UTC → enrich_movies_with_tmdb() runs
           ├─ Finds all movies where tmdb_id IS NULL (8 movies from above)
           ├─ Creates TMDBClient
           ├─ For each movie:
           │  ├─ Searches TMDB by title
           │  ├─ Updates movie with TMDB data
           │  └─ Saves to database
           └─ Logs: "7 enriched, 1 not found" (example)

Throughout the day:
           ├─ Users can visit /movies/ to see the list
           ├─ Views query the Movie model
           └─ Display updated movies in real-time
```

---

## Data Flow Diagram

```
YouTube Channels (RottenTomatoes, MUBI)
    ↓
RottenTomatoesClient / MubiClient (in contrib/youtube/)
    ↓
fetch_rotten_tomatoes_videos() / fetch_mubi_videos() tasks
    ↓
_fetch_and_save_videos() helper
    ↓
Movie.objects.create() → Database
    ↓
Movies with tmdb_id=NULL
    ↓
enrich_movies_with_tmdb() task
    ↓
TMDBClient (in contrib/tmdb/)
    ↓
Movie.save() → Database
    ↓
Movies with TMDB metadata
    ↓
movie_list(request) view
    ↓
movie_list.html template
    ↓
User sees the list in web browser
```

---

## Key Implementation Details

### Duplicate Prevention Strategy

When fetching videos, duplicates are prevented by checking if a movie with the same title already exists:

```python
existing_movie = Movie.objects.filter(title=video['title']).first()
if existing_movie:
    skipped_count += 1
    continue
```

**Limitations:**
- Only checks `title` field (case-sensitive, exact match)
- Doesn't handle title variations (e.g., "Star Wars" vs "Star Wars: Episode IV")
- Doesn't use `tmdb_id` or `imdb_id` for duplicate detection

### Enrichment-as-Second-Pass Pattern

Movies are created in two stages:

**Stage 1: Fetch (immediate)**
```python
Movie.objects.create(
    title=video['title'],
    original_title=video['original_title'],
    video_id=video['video_id'],
    source=source_name
    # tmdb_id is NULL
)
```

**Stage 2: Enrich (later)**
```python
movie.tmdb_id = tmdb_data.get('id')
movie.overview = tmdb_data.get('overview')
# ... other fields
movie.save()
```

**Why This Pattern?**
- Fetching is fast (just parses YouTube metadata)
- Enrichment is slow (requires TMDB API calls)
- Separating them allows faster data availability
- Enrichment can be run separately and retried independently

### Error Handling Levels

**Task Level:**
```python
except Exception as e:
    logger.error(f"Error in enrich_movies_with_tmdb: {e}", exc_info=True)
    raise  # Triggers Dramatiq retry (up to 3 times)
```

**Movie Level:**
```python
except Exception as e:
    logger.error(f"Error enriching {movie.title}: {e}")
    continue  # Skip this movie but process others
```

This ensures:
- One bad movie doesn't break the entire enrichment task
- If the whole task fails, Dramatiq will retry it

---

## Performance Characteristics

### View Performance

**`movie_list()` view:**
```python
movies = Movie.objects.all().order_by('-created_at')  # Query 1: All movies
context = {
    'movies': movies,
    'total_movies': movies.count(),  # Query 2: Count
    'enriched_movies': movies.filter(tmdb_id__isnull=False).count(),  # Query 3: Count
}
```

**SQL Queries:** 3 queries
- 1 to fetch all movies
- 1 to count total
- 1 to count enriched

**Optimization Opportunity:**
Could use `annotate()` to count in a single query:
```python
from django.db.models import Count, Q

movies = Movie.objects.all()
stats = {
    'total': movies.count(),
    'enriched': movies.filter(tmdb_id__isnull=False).count()
}
```

### Task Performance

**`_fetch_and_save_videos()` task:**
- Time: O(n) where n = number of videos fetched
- For each video: 1 query to check duplicates + 1 query to create movie = 2n queries
- Scales slowly with large result sets

**`enrich_movies_with_tmdb()` task:**
- Time: O(m) where m = number of unenriched movies
- For each movie: 1 TMDB API call + 1 database query to save = ~2m API calls + m queries
- Dominated by TMDB API latency, not database queries

---

## Testing Considerations

### Unit Tests (for models)

```python
def test_movie_creation():
    movie = Movie.objects.create(
        title="Dune",
        source="rotten_tomatoes"
    )
    assert movie.tmdb_id is None
    assert movie.created_at is not None
```

### Integration Tests (for tasks)

```python
def test_fetch_saves_movies():
    # Mock YouTube client
    # Run fetch task
    # Assert movies created in database
    # Assert no duplicates
```

### View Tests

```python
def test_movie_list_view():
    Movie.objects.create(title="Dune", source="rotten_tomatoes", tmdb_id=438631)
    Movie.objects.create(title="Blade Runner", source="mubi")

    response = client.get('/movies/')
    assert response.status_code == 200
    assert 'total_movies' in response.context
    assert response.context['total_movies'] == 2
    assert response.context['enriched_movies'] == 1
```

---

## Summary

The movies app implements a three-stage data pipeline:

1. **Fetch Stage** (hourly): Pull videos from YouTube channels, save as unenriched movies
2. **Enrich Stage** (hourly): Look up TMDB data, update movies with metadata
3. **Display Stage** (on-demand): Show movies to users via web views

Each file has a specific role:
- **models.py**: Defines what a movie is
- **views.py**: Handles user requests, queries movies, renders HTML
- **tasks.py**: Runs background jobs to fetch and enrich data
- **urls.py**: Maps URLs to views
- **admin.py**: Provides admin interface for manual movie management
- **apps.py**: Configures the Django app
