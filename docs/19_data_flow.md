# 19. Data Flow Architecture

Complete journey of data from YouTube → Database → Web Display

## The 3-Stage Data Pipeline

```
STAGE 1: FETCH
  YouTube API
  ↓
  Extract titles & video IDs
  ↓
  STAGE 2: SAVE
    Database
    ↓
    Create Movie records
    ↓
    STAGE 3: ENRICH
      TMDB API
      ↓
      Add metadata
      ↓
      Update Movie records
      ↓
      STAGE 4: DISPLAY
        Web Browser
        ↓
        Show movies to user
```

---

## Stage 1: Fetch from YouTube

### Time: Daily 00:00 UTC (Midnight)

```
Task: fetch_rotten_tomatoes_videos()
  Location: movies/tasks.py
  Schedule: @cron('0 0 * * *')
```

### Detailed Flow

```
1. TASK STARTS
   ├─ Entry point: fetch_rotten_tomatoes_videos()
   └─ Location: movies/tasks.py:70-80

2. CREATE CLIENT
   ├─ Code: RottenTomatoesClient()
   ├─ Location: contrib/youtube/api.py:157-198
   └─ Result: Client object

3. FETCH VIDEOS
   ├─ Code: client.get_videos() → get_data()
   ├─ Calls: YouTubeBaseClient._fetch_videos()
   ├─ Location: contrib/youtube/api.py:46-89
   └─ API used: yt-dlp (YouTube scraper)

4. EXTRACT TITLES
   ├─ Code: YouTubeBaseClient._extract_title_and_id()
   ├─ Location: contrib/youtube/api.py:106-139
   ├─ What it does:
   │  ├─ Calls _clean_title() for each video
   │  ├─ RottenTomatoesClient._clean_title(): "Title Official Trailer #1 (2025)" → "Title"
   │  ├─ Filters out teasers (returns None)
   │  └─ Extracts year from title
   └─ Result: [
      {'title': 'Dune', 'year': 2021, 'original_title': '...', 'video_id': 'abc123'},
      {'title': 'Inception', 'year': 2010, 'original_title': '...', 'video_id': 'xyz789'}
    ]

5. RETURN TO TASK
   └─ Result: cleaned video list (2 movies, teasers filtered)
```

### Code Example

```python
# movies/tasks.py (Task orchestration)
@dramatiq.actor(max_retries=3)
@cron('0 0 * * *')
def fetch_rotten_tomatoes_videos():
    client = RottenTomatoesClient()  # ← Create client
    _fetch_and_save_videos(client, 'rotten_tomatoes')  # ← Save to DB
```

```python
# contrib/youtube/api.py (Client logic)
class RottenTomatoesClient(YouTubeBaseClient):
    CHANNEL_URL = "https://www.youtube.com/@RottenTomatoesIndie/videos"

    def get_videos(self):
        return self.get_data()  # ← Start pipeline

    def _clean_title(self, title):
        # "The Lord of the Rings Official Trailer #1 (2025)" → "The Lord of the Rings"
        if 'Trailer #' not in title:
            return None  # Skip teasers
        match = re.match(r'^(.+?)\s+(?:Official\s+)?Trailer\s+#', title)
        return match.group(1).strip() if match else None
```

### API Response Example

**YouTube API returns:**
```json
{
  "entries": [
    {
      "title": "The Lord of the Rings Official Trailer #1 (2025)",
      "id": "abc123",
      "description": "Official trailer",
      "upload_date": "20250101"
    },
    {
      "title": "Avatar Official Teaser (2025)",
      "id": "skip123",
      "description": "Teaser"
    }
  ]
}
```

**WhichMovie processes to:**
```python
[
    {
        'title': 'The Lord of the Rings',  # Cleaned
        'year': 2025,  # Extracted
        'original_title': 'The Lord of the Rings Official Trailer #1 (2025)',
        'video_id': 'abc123'
    }
    # Avatar teaser is NOT included (filtered)
]
```

---

## Stage 2: Save to Database

### Time: Immediately after fetch (still 00:00-01:00 UTC)

```
Function: _fetch_and_save_videos()
  Location: movies/tasks.py:17-67
```

### Detailed Flow

```
1. GET VIDEOS
   └─ Receive from fetch stage: [2 cleaned movies]

2. CHECK EACH VIDEO
   ├─ For each movie:
   │  ├─ Query: Movie.objects.filter(title='Dune')
   │  ├─ Found? → Skip (duplicate)
   │  └─ Not found? → Continue to create

3. CREATE MOVIE RECORDS
   ├─ Code: Movie.objects.create(...)
   ├─ Location: movies/models.py (Movie model)
   ├─ What gets saved:
   │  ├─ title: 'Dune'
   │  ├─ original_title: 'Dune Official Trailer #1 (2021)'
   │  ├─ video_id: 'abc123'
   │  ├─ source: 'rotten_tomatoes'
   │  ├─ tmdb_id: NULL (not enriched yet)
   │  ├─ imdb_id: NULL
   │  ├─ overview: NULL
   │  ├─ release_date: NULL
   │  ├─ poster_path: NULL
   │  ├─ backdrop_path: NULL
   │  ├─ created_at: 2025-11-21 00:05:00
   │  └─ updated_at: 2025-11-21 00:05:00

4. LOG RESULTS
   └─ "Created: 1, Skipped: 0"
```

### Code Example

```python
# movies/tasks.py
def _fetch_and_save_videos(client, source_name):
    """Fetch videos and save to database"""
    videos = client.get_videos()  # ← Get cleaned videos

    for video in videos:
        # Check if already exists
        existing_movie = Movie.objects.filter(
            title=video['title']
        ).first()

        if existing_movie:
            logger.info(f"[SKIPPED] {video['title']} already exists")
            continue

        # Create new movie
        movie = Movie.objects.create(
            title=video['title'],
            original_title=video['original_title'],
            video_id=video['video_id'],
            source=source_name  # 'rotten_tomatoes' or 'mubi'
        )
        logger.info(f"[CREATED] {movie.title}")
```

### Database Insert Example

**Generated SQL:**
```sql
INSERT INTO movies_movie (
    title, original_title, video_id, source,
    created_at, updated_at
) VALUES (
    'Dune', 'Dune Official Trailer #1 (2021)', 'abc123', 'rotten_tomatoes',
    '2025-11-21 00:05:00', '2025-11-21 00:05:00'
);

Result: Movie with id=1
```

**Django ORM equivalent:**
```python
movie = Movie.objects.create(
    title='Dune',
    original_title='Dune Official Trailer #1 (2021)',
    video_id='abc123',
    source='rotten_tomatoes'
)
```

### Multiple Fetch Sources

**00:00 UTC** - RottenTomatoesClient
```
Fetch from: https://www.youtube.com/@RottenTomatoesIndie/videos
Format: "Movie Official Trailer #1 (2025)"
Example movies: Dune, Inception, Avatar
```

**01:00 UTC** - MubiClient
```
Fetch from: https://www.youtube.com/@mubi/videos
Format: "MOVIE | Official Trailer #1"
Example movies: Arrival, Blade Runner 2049, Oppenheimer
```

---

## Stage 3: Enrich with TMDB

### Time: Daily 02:00 UTC

```
Task: enrich_movies_with_tmdb()
  Location: movies/tasks.py:96-152
  Schedule: @cron('0 2 * * *')
```

### Detailed Flow

```
1. FIND UNENRICHED MOVIES
   ├─ Query: Movie.objects.filter(tmdb_id__isnull=True)
   ├─ Result: 2 movies (both from fetch stage, no tmdb_id yet)
   └─ Database query:
      SELECT * FROM movies_movie WHERE tmdb_id IS NULL

2. CREATE TMDB CLIENT
   ├─ Code: TMDBClient()
   ├─ Location: contrib/tmdb/api.py
   └─ Requires: TMDB_API_KEY environment variable

3. FOR EACH UNENRICHED MOVIE
   ├─ Movie 1: 'Dune'
   │  ├─ Code: client.search_movie('Dune')
   │  ├─ API request: GET /search/movie?query=Dune&api_key=...
   │  ├─ TMDB API returns:
   │  │  {
   │  │    "id": 438631,
   │  │    "title": "Dune",
   │  │    "release_date": "2021-10-22",
   │  │    "overview": "Paul Atreides travels to...",
   │  │    "poster_path": "/68zzG5er0nX7K51PNIuCNsd1qKc.jpg",
   │  │    "backdrop_path": "/n6bUvigpRFqSwmPp1PQoD6EEMT9.jpg"
   │  │  }
   │  │
   │  ├─ Get IMDb ID: client._get_imdb_id(438631)
   │  │  └─ TMDB API: GET /movie/438631/external_ids?api_key=...
   │  │  └─ Returns: "tt0330373"
   │  │
   │  └─ Update Movie record:
   │     movie.tmdb_id = 438631
   │     movie.imdb_id = 'tt0330373'
   │     movie.overview = 'Paul Atreides travels to...'
   │     movie.release_date = '2021-10-22'
   │     movie.poster_path = '/68zzG5er0nX7K51PNIuCNsd1qKc.jpg'
   │     movie.backdrop_path = '/n6bUvigpRFqSwmPp1PQoD6EEMT9.jpg'
   │     movie.save()
   │
   └─ Movie 2: 'Inception'
      └─ Same process...

4. HANDLE NOT FOUND
   └─ If TMDB doesn't have the movie:
      └─ Log: "Not found on TMDB: Some Obscure Movie"
      └─ Continue (don't crash)

5. LOG RESULTS
   └─ "Enriched: 2, Not found: 0"
```

### Code Example

```python
# movies/tasks.py
@dramatiq.actor(max_retries=3)
@cron('0 2 * * *')
def enrich_movies_with_tmdb():
    # Find unenriched
    unenriched = Movie.objects.filter(tmdb_id__isnull=True)

    if not unenriched.exists():
        logger.info("No unenriched movies")
        return

    client = TMDBClient()  # ← Create TMDB client
    enriched_count = 0

    for movie in unenriched:
        # Search TMDB
        tmdb_data = client.search_movie(movie.title)

        if not tmdb_data:
            logger.warning(f"Not found: {movie.title}")
            continue

        # Update movie with TMDB data
        movie.tmdb_id = tmdb_data['id']
        movie.imdb_id = tmdb_data.get('imdb_id')
        movie.overview = tmdb_data.get('overview')
        movie.release_date = tmdb_data.get('release_date')
        movie.poster_path = tmdb_data.get('poster_path')
        movie.backdrop_path = tmdb_data.get('backdrop_path')
        movie.save()

        enriched_count += 1
        logger.info(f"Enriched: {movie.title}")

    logger.info(f"Total enriched: {enriched_count}")
```

### Database Update Example

**Before enrichment:**
```sql
id | title | tmdb_id | imdb_id | overview | release_date
1  | Dune  | NULL    | NULL    | NULL     | NULL
```

**After enrichment:**
```sql
id | title | tmdb_id | imdb_id   | overview              | release_date
1  | Dune  | 438631  | tt0330373 | Paul Atreides travels...| 2021-10-22
```

---

## Stage 4: Display to User

### Time: Any time user visits the website

```
View: movie_list()
  Location: movies/views.py:1-15
  URL: /movies/
```

### Detailed Flow

```
1. USER VISITS WEBSITE
   └─ Browser: GET http://localhost:8000/movies/

2. REQUEST ARRIVES AT DJANGO
   ├─ Middleware pipeline processes request
   ├─ URL routing matches /movies/ → movie_list view
   └─ View function executes

3. VIEW QUERIES DATABASE
   ├─ Code: movies = Movie.objects.all().order_by('-created_at')
   ├─ Query:
   │  SELECT * FROM movies_movie
   │  ORDER BY created_at DESC
   └─ Result: QuerySet of 42 movies (latest first)

4. VIEW RENDERS TEMPLATE
   ├─ Code: render(request, 'movies/movie_list.html', {'movies': movies})
   ├─ Template receives: {'movies': [Movie1, Movie2, ...]}
   └─ Template file: templates/movies/movie_list.html

5. TEMPLATE LOOPS THROUGH MOVIES
   ├─ For each movie in movies:
   │  ├─ Display: {{ movie.title }}
   │  ├─ Display: {{ movie.poster_path }}
   │  ├─ Display: {{ movie.overview }}
   │  ├─ Display: {{ movie.release_date }}
   │  └─ Link to: /movies/{{ movie.id }}/
   └─ Generate HTML with all 42 movies

6. RESPONSE SENT TO BROWSER
   ├─ HTTP 200 OK
   ├─ Content-Type: text/html
   └─ Body: HTML page with 42 movies listed

7. BROWSER RENDERS HTML
   └─ User sees: Movie list with posters, titles, plots, etc.
```

### Code Example

```python
# movies/views.py
def movie_list(request):
    # Query database
    movies = Movie.objects.all().order_by('-created_at')

    context = {
        'movies': movies,
        'total_movies': movies.count(),
        'enriched_movies': movies.filter(tmdb_id__isnull=False).count(),
    }

    # Render template
    return render(request, 'movies/movie_list.html', context)
```

### Template Example

```html
<!-- templates/movies/movie_list.html -->
<h1>Movie List</h1>
<p>Total: {{ total_movies }} | Enriched: {{ enriched_movies }}</p>

<div class="movie-grid">
    {% for movie in movies %}
    <div class="movie-card">
        {% if movie.poster_path %}
        <img src="{{ movie.poster_path }}" alt="{{ movie.title }}">
        {% endif %}

        <h2>{{ movie.title }}</h2>

        {% if movie.release_date %}
        <p>Released: {{ movie.release_date|date:"Y" }}</p>
        {% endif %}

        {% if movie.overview %}
        <p>{{ movie.overview|truncatewords:20 }}</p>
        {% endif %}

        <p>Source: {{ movie.source }}</p>

        <a href="{% url 'movie_detail' movie.id %}">View Details</a>
    </div>
    {% endfor %}
</div>
```

---

## Complete Timing Diagram

```
TIME    STAGE               ACTION
────────────────────────────────────────────────────
00:00   Fetch RT Videos     Task starts → YouTube → DB (2 movies)
00:05   Fetch Mubi Videos   Task starts → YouTube → DB (3 movies)
01:00   Enrich TMDB         Task starts → 5 movies → TMDB enrichment
02:00   Ready for Display   All data ready in database
...
12:00   User visits         Browser → View → Template → Movies displayed
12:01   User clicks movie   Browser → Detail view → Full movie info
```

## Data Transformation Pipeline

```
YouTube API Response
├─ Format: Raw JSON from yt-dlp
├─ Example:
│  {
│    "title": "The Lord of the Rings Official Trailer #1 (2025)",
│    "id": "abc123",
│    "description": "..."
│  }
│
↓ _clean_title() & _extract_title_and_id()
│
Cleaned Video Data
├─ Format: Python dictionary
├─ Example:
│  {
│    'title': 'The Lord of the Rings',
│    'year': 2025,
│    'original_title': 'The Lord of the Rings Official Trailer #1 (2025)',
│    'video_id': 'abc123'
│  }
│
↓ Movie.objects.create()
│
Database Movie Record
├─ Format: PostgreSQL row
├─ Example:
│  id: 1
│  title: 'The Lord of the Rings'
│  video_id: 'abc123'
│  source: 'rotten_tomatoes'
│  tmdb_id: NULL (not enriched yet)
│
↓ client.search_movie() & movie.save()
│
Enriched Database Record
├─ Format: PostgreSQL row (updated)
├─ Example:
│  id: 1
│  title: 'The Lord of the Rings'
│  tmdb_id: 121 (now enriched)
│  imdb_id: 'tt0120737'
│  overview: 'In a fantasy realm...'
│  release_date: '2001-12-19'
│  poster_path: '/url/to/poster.jpg'
│
↓ Template rendering
│
HTML Display
└─ User sees movie with all details
```

---

Next: [API Clients](./20_api_clients.md)
