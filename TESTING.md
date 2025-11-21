# Testing Guide

## 1. Test Structure

### Test Files Location

```
contrib/youtube/tests/
├── test_rotten_tomatoes_client.py  (12 tests implemented)
├── test_mubi_client.py             (12 tests implemented)
└── test_youtube_integration.py     (11 test stubs)

contrib/tmdb/tests/
└── test_tmdb_client.py             (17 test stubs)

movies/
├── tests_models.py                 (24 test stubs)
└── tests_tasks.py                  (20 test stubs)
```

### What Each Test File Tests

#### `test_rotten_tomatoes_client.py` - ✅ 12 tests implemented

**Purpose:** Test the RottenTomatoesClient YouTube channel integration

**What it tests:**
- `_clean_title()` - Parsing "Movie Title Official Trailer #1 (2025)" format to extract just "Movie Title"
- `_extract_title_and_id()` - Combining title cleaning with filtering (removes teasers)
- `_fetch_videos()` - API extraction from mocked YouTube data

**Test classes:**
- `TestRottenTomatoesClientCleanTitle` - 4 tests for title parsing
- `TestRottenTomatoesClientExtractTitleAndId` - 2 tests for filtering
- `TestRottenTomatoesClientFetchVideos` - 1 test for API extraction

**Example scenarios tested:**
- Extract "The Lord of the Rings" from "The Lord of the Rings Official Trailer #1 (2025)"
- Skip teaser videos (those with "Official Teaser" instead of "Trailer #")
- Handle videos without trailer pattern

---

#### `test_mubi_client.py` - ✅ 12 tests implemented

**Purpose:** Test the MubiClient YouTube channel integration

**What it tests:**
- `_clean_title()` - Parsing "MOVIE TITLE | Official Trailer #1" format
- `_extract_title_and_id()` - Combining title cleaning with filtering
- `_fetch_videos()` - API extraction from mocked YouTube data

**Test classes:**
- `TestMubiClientCleanTitle` - 4 tests for title parsing (pipe-separated format)
- `TestMubiClientExtractTitleAndId` - 2 tests for filtering
- `TestMubiClientFetchVideos` - 1 test for API extraction

**Example scenarios tested:**
- Extract "DUNE" from "DUNE | Official Trailer #1"
- Handle "In Cinemas Now" suffix removal
- Skip teaser videos

---

#### `test_youtube_integration.py` - ⏳ 11 test stubs

**Purpose:** Test the complete YouTube data flow (full pipeline integration)

**What it will test:**
- `get_data()` method - The full pipeline: fetch videos from YouTube → parse titles → filter non-trailers → return cleaned data
- Edge cases: empty channels, all teasers, missing data
- Data preservation: video IDs, years, original titles

**Test classes:**
- `TestRottenTomatoesClientIntegration` - 5 tests for complete RottenTomatoes flow
- `TestMubiClientIntegration` - 4 tests for complete Mubi flow
- `TestYouTubeClientsComparison` - 2 tests comparing both clients

**Example scenarios to test:**
- Full pipeline: 3 videos from API (2 valid + 1 teaser) → should return 2 cleaned videos
- All teasers: channel with only teaser videos → should return empty list
- Empty channel: no videos available → should raise NetworkError

---

#### `test_tmdb_client.py` - ⏳ 17 test stubs

**Purpose:** Test the TMDBClient for movie enrichment

**What it will test:**
- `search_movie()` - Search TMDB by title and optional year
- `_get_imdb_id()` - Fetch IMDb ID from TMDB movie ID
- `get_data()` - Main interface method
- Configuration validation and error handling

**Test classes:**
- `TestTMDBClientSearchMovie` - 4 tests for search functionality
- `TestTMDBClientGetImdbId` - 2 tests for IMDb ID fetching
- `TestTMDBClientGetData` - 3 tests for public interface
- `TestTMDBClientValidation` - 3 tests for config validation
- `TestTMDBClientNetworkErrors` - 2 tests for error handling

**Example scenarios to test:**
- Search "Star Wars" → find movie ID 11 with metadata (release_date, overview, poster)
- Search with year filter "Dune 2021" → return 2021 version, not 1984
- Movie not found → return None gracefully
- API timeout → raise NetworkError

---

#### `tests_models.py` - ⏳ 24 test stubs

**Purpose:** Test the Movie Django model

**What it will test:**
- Field validation (required vs optional)
- Unique constraints (tmdb_id, imdb_id must be unique)
- Field types and max lengths
- Auto-generated timestamps (created_at, updated_at)
- Database queries and filtering

**Test classes:**
- `TestMovieModel` - 3 tests for basic model operations
- `TestMovieFieldValidation` - 6 tests for field constraints
- `TestMovieFieldTypes` - 5 tests for field types and lengths
- `TestMovieTimestamps` - 3 tests for auto-generated dates
- `TestMovieEdgeCases` - 3 tests for unusual scenarios
- `TestMovieQueryingAndFiltering` - 4 tests for database queries

**Example scenarios to test:**
- Create movie with required fields (title, video_id, source)
- Unique constraint: two movies with same tmdb_id → should fail
- Filter by source: get all 'rotten_tomatoes' vs 'mubi' movies
- Auto-timestamp: created_at and updated_at set correctly

---

#### `tests_tasks.py` - ⏳ 20 test stubs

**Purpose:** Test the Dramatiq cron tasks that orchestrate everything

**What it will test:**
- `_fetch_and_save_videos()` - Helper function that saves YouTube videos to database
- `fetch_rotten_tomatoes_videos()` - Task that runs daily at midnight
- `fetch_mubi_videos()` - Task that runs daily at 1 AM
- `enrich_movies_with_tmdb()` - Task that enriches unenriched movies with TMDB data

**Test classes:**
- `TestFetchAndSaveVideos` - 7 tests for database save logic
- `TestFetchRottenTomatoesVideos` - 3 tests for RottenTomatoes task
- `TestFetchMubiVideos` - 2 tests for Mubi task
- `TestEnrichMoviesWithTmdb` - 8 tests for TMDB enrichment task

**Example scenarios to test:**
- Fetch 2 videos from YouTube → create 2 Movie records in database
- Duplicate detection: video already exists by title → skip (don't duplicate)
- Enrichment: 3 unenriched movies → search TMDB for each → update with tmdb_id, overview, poster_path
- Movie not found in TMDB → log "not found" and continue
- Task scheduling: RottenTomatoes at midnight, Mubi at 1 AM, enrichment at 2 AM

---

## 5. Fixtures & Mocking

### Why We Mock

- **Avoid slow network calls** - Real YouTube/TMDB API would be 5-10 seconds
- **Avoid flaky tests** - API might be down or rate-limited
- **Consistent results** - Same data every time the test runs

### Mock Data Examples

**YouTube API Mock** (`conftest.py`):
```python
@pytest.fixture
def mock_yt_dlp_rotten_tomatoes_response():
    return {
        'entries': [
            {'title': 'The Lord of the Rings Official Trailer #1 (2025)', 'id': 'abc123'},
            {'title': 'Avatar Official Teaser (2025)', 'id': 'skip123'}  # Teaser
        ]
    }
```
