# 1. Platform Overview

## What is WhichMovie App?

WhichMovie is a Django web application that automatically fetches movie trailers from YouTube channels and enriches them with metadata from TMDB (The Movie Database).

## What Does It Do?

The app has a **3-stage pipeline**:

```
STAGE 1: FETCH
  YouTube Channels (RottenTomatoes, Mubi)
  → Extract trailer titles & video IDs
  
STAGE 2: SAVE
  Database Storage
  → Create Movie records

STAGE 3: ENRICH
  TMDB API
  → Add metadata (year, plot, poster, rating)
```

## Key Features

### 1. YouTube Video Fetching
- Monitors two YouTube channels:
  - **RottenTomatoes Indie** - Official trailer channel
  - **Mubi** - Art house cinema channel
- Extracts movie titles from trailer titles
- Filters out teasers (only wants official trailers)

### 2. Duplicate Detection
- Checks if movie already exists in database
- Prevents duplicate entries by title
- Only saves new movies

### 3. TMDB Enrichment
- Searches The Movie Database for each movie
- Adds metadata:
  - IMDb ID
  - Release date
  - Plot summary
  - Poster image
  - Backdrop image

### 4. Web Interface
- Lists all collected movies
- Shows which are enriched vs not
- Displays movie metadata (poster, year, plot)

## Technology Stack

```
Backend:        Django (Python web framework)
Database:       PostgreSQL (data storage)
Tasks:          Dramatiq (background job scheduler)
Video API:      yt-dlp (YouTube video scraper)
Movie API:      TMDB API v3 (movie metadata)
Frontend:       Django Templates + HTML/CSS
Testing:        pytest (testing framework)
```

## Data Model

```
Movie (Database Table)
├── title              (e.g., "Dune")
├── original_title     (e.g., "Dune Official Trailer #1 (2021)")
├── video_id           (YouTube ID, e.g., "abc123")
├── source             ("rotten_tomatoes" or "mubi")
├── tmdb_id            (TMDB database ID)
├── imdb_id            (IMDb ID)
├── overview           (Movie plot summary)
├── release_date       (e.g., "2021-10-22")
├── poster_path        (URL to poster image)
├── backdrop_path      (URL to backdrop image)
├── created_at         (When added to database)
└── updated_at         (When last updated)
```

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    WHICHMOVIE APPLICATION                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐                                          │
│  │   Web Browser    │ ← User visits website                    │
│  └────────┬─────────┘                                          │
│           │                                                    │
│           ↓                                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Django Web Server (runserver)                    │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ URL Router → View → Template → Response            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                              │ 
│                 ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        PostgreSQL Database                               │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Movie Table (title, tmdb_id, video_id, etc)        │  │  │
│  │  │ User Table (admin users)                           │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Background Tasks (Dramatiq)                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Task 1: Fetch RottenTomatoes videos (Daily 00:00)  │  │  │
│  │  │ Task 2: Fetch Mubi videos (Daily 01:00)            │  │  │
│  │  │ Task 3: Enrich with TMDB (Daily 02:00)             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──┬───────────────────────────────────────────────────────┘  │
│     │                                                          │
│     ├→ yt-dlp (YouTube API)                                    │
│     └→ TMDB API                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Key Components

### Apps (Django modules)

1. **whichmovie** (Project)
   - Main configuration
   - Settings, URLs, WSGI

2. **movies** (App)
   - Core business logic
   - Models, views, tasks
   - Movie management

3. **contrib.youtube** (Reusable component)
   - YouTube video fetching
   - Title parsing
   - RottenTomatoesClient, MubiClient

4. **contrib.tmdb** (Reusable component)
   - TMDB movie search
   - Metadata enrichment
   - TMDBClient

5. **contrib.base** (Abstract base classes)
   - BaseClient interface
   - Common error types

## Daily Workflow

```
00:00 (Midnight UTC)
  ↓
fetch_rotten_tomatoes_videos() task starts
  ├→ Fetch videos from RottenTomatoes channel
  ├→ Parse titles
  └→ Save to database

01:00 (1 AM UTC)
  ↓
fetch_mubi_videos() task starts
  ├→ Fetch videos from Mubi channel
  ├→ Parse titles
  └→ Save to database

02:00 (2 AM UTC)
  ↓
enrich_movies_with_tmdb() task starts
  ├→ Find unenriched movies
  ├→ Search TMDB for each
  └→ Update with metadata
```

## File Structure

```
whichmovie_app/
├── whichmovie/          (Project settings)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── movies/              (Main app)
│   ├── models.py        (Movie model)
│   ├── views.py         (Web views)
│   ├── urls.py          (URL routing)
│   ├── tasks.py         (Background tasks)
│   └── admin.py         (Admin interface)
│
├── contrib/             (Reusable components)
│   ├── youtube/         (YouTube fetching)
│   ├── tmdb/            (TMDB enrichment)
│   └── base/            (Abstract classes)
│
├── templates/           (HTML templates)
├── static/              (CSS, JavaScript, images)
├── manage.py            (Django CLI)
└── pytest.ini           (Test configuration)
```

---

Next: [Django Basics](./02_django_basics.md)
