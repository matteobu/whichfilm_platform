# Contrib Package - External Service Integrations

A collection of reusable client libraries and utilities for integrating with external APIs (YouTube, TMDB, etc).

---

## Overview

The `contrib` package provides:
1. **Base abstractions** for building API clients
2. **YouTube client** for fetching video metadata from channels
3. **TMDB client** for fetching movie metadata
4. **Utility functions** for rate limiting, retries, caching, and error handling

## Architecture

```
contrib/
├── base/              # Abstract base classes and exceptions
│   ├── client.py      # BaseClient abstract class
│   └── exceptions.py  # Exception hierarchy
├── youtube/           # YouTube channel integrations
│   ├── api.py         # YouTubeBaseClient, RottenTomatoesClient, MubiClient
│   └── tests/         # Unit and integration tests
├── tmdb/              # TMDB API integration
│   ├── api.py         # TMDBClient
│   └── tests/         # Unit and integration tests
├── utils/             # Reusable utilities
│   ├── rate_limiter.py   # RateLimiter class
│   ├── decorators.py     # @retry, @cached decorators
│   └── helpers.py        # Helper functions
└── __init__.py        # Package initialization
```

---

## `base/client.py` - Abstract Base Client

**Purpose:** Define the interface that all external service clients must implement.

### BaseClient Class

```python
class BaseClient(ABC):
    """
    Abstract base class for all external service clients.
    Subclasses should implement the specific API interaction logic.
    """

    def __init__(self):
        """Initialize the client."""
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """
        Validate that the client is properly configured.
        Should raise ValidationError if configuration is invalid.
        """
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """
        Fetch data from the external service.
        Subclasses must implement their specific data fetching logic.
        """
        pass
```

**Key Design Principles:**

1. **Validation-on-Init Pattern**
   - `_validate_config()` is called in `__init__`
   - Fails fast if configuration is missing (API keys, URLs, etc.)
   - Prevents silent failures during task execution

2. **Abstract Methods**
   - `_validate_config()`: Ensures API keys/credentials are present
   - `get_data()`: Main method for fetching data from external service

3. **Inheritance Pattern**
   - All clients inherit from BaseClient
   - Forces implementation of abstract methods
   - Ensures consistent error handling

**Usage Example:**

```python
from contrib.base import BaseClient, ValidationError

class MyClient(BaseClient):
    def _validate_config(self):
        if not self.api_key:
            raise ValidationError("API key required")

    def get_data(self, **kwargs):
        # Fetch data from external API
        return data
```

---

## `base/exceptions.py` - Exception Hierarchy

**Purpose:** Define custom exceptions for error handling across all clients.

```python
class ClientError(Exception):
    """Base exception for client errors."""
    pass

class RateLimitError(ClientError):
    """Raised when rate limit is exceeded."""
    pass

class ValidationError(ClientError):
    """Raised when input validation fails."""
    pass

class NetworkError(ClientError):
    """Raised when network request fails."""
    pass

class NotFoundError(ClientError):
    """Raised when resource is not found."""
    pass
```

**Exception Hierarchy:**

```
Exception
└── ClientError
    ├── RateLimitError       # API rate limit exceeded
    ├── ValidationError      # Configuration/input validation failed
    ├── NetworkError         # HTTP request failed, timeout, etc.
    └── NotFoundError        # Resource not found (404)
```

**Usage Pattern:**

```python
try:
    videos = client.get_videos()
except ValidationError:
    # Handle missing API key or invalid input
except NetworkError:
    # Handle HTTP errors, timeouts, connection issues
except RateLimitError:
    # Handle API rate limits
```

**Benefits:**

- Specific exception handling for different error types
- Easy to retry on specific errors (e.g., NetworkError but not ValidationError)
- Consistent error handling across all clients

---

## `youtube/api.py` - YouTube Client for Fetching Videos

**Purpose:** Fetch video metadata from YouTube channels using yt-dlp.

### YouTubeBaseClient - Base Implementation

```python
class YouTubeBaseClient(BaseClient):
    """
    Base class for YouTube channel clients.
    Provides common functionality for fetching videos from YouTube channels using yt-dlp.
    Subclasses override _clean_title() to handle channel-specific title formats.
    """

    CHANNEL_URL = None      # Override in subclasses
    CHANNEL_ID = None       # Fallback for backward compatibility

    def _validate_config(self):
        """Validate that CHANNEL_URL or CHANNEL_ID is defined."""
        if not self.CHANNEL_URL and not self.CHANNEL_ID:
            raise ValidationError("YouTube CHANNEL_URL or CHANNEL_ID is required")

    def _get_channel_url(self):
        """Return the channel URL for yt-dlp extraction."""
        if self.CHANNEL_URL:
            return self.CHANNEL_URL
        return f"https://www.youtube.com/channel/{self.CHANNEL_ID}"

    def _fetch_videos(self):
        """Fetch raw video data from YouTube using yt-dlp."""
        # Uses yt-dlp to extract videos from channel
        # Returns list of video dicts with:
        # - title: Raw YouTube title
        # - description: Video description
        # - published: Upload date
        # - video_url: YouTube URL
        # - video_id: YouTube video ID
        # - thumbnail: Thumbnail image URL

    def _extract_year(self, title):
        """Extract year from title using regex (YYYY) format."""
        # Looks for 4-digit year in parentheses
        # Returns: int or None

    def _extract_title_and_id(self, videos):
        """
        Process raw videos into cleaned format.

        For each video:
        1. Extract original_title (raw YouTube title)
        2. Call _clean_title() (channel-specific cleaning)
        3. Extract year from original_title
        4. Get video_id

        Returns: List of dicts with title, year, original_title, video_id
        """

    def get_data(self, **kwargs):
        """Main method: fetch and parse YouTube videos."""
        videos = self._fetch_videos()
        processed_videos = self._extract_title_and_id(videos)
        return processed_videos
```

**Key Features:**

1. **yt-dlp Integration**
   - Uses `extract_flat='in_playlist'` to get video list without downloading
   - Fast extraction of metadata
   - Handles pagination automatically

2. **Two-Step Processing**
   - `_fetch_videos()`: Get raw data from YouTube
   - `_extract_title_and_id()`: Process and clean data

3. **Extensibility**
   - Subclasses override `_clean_title()` for channel-specific formatting
   - Base class handles common logic (fetch, extract year, get video_id)

### RottenTomatoesClient - RottenTomatoes Channel

```python
class RottenTomatoesClient(YouTubeBaseClient):
    """
    RottenTomatoes INDIE channel client.
    Handles title format: "Movie Title Official Trailer #1 (2025)"
    Only processes official trailers (Trailer #), skips teasers.
    """

    CHANNEL_URL = "https://www.youtube.com/@RottenTomatoesIndie/videos"
    CHANNEL_ID = "UCLyYEq4ODlw3OD9qhGqwimw"  # Fallback

    def _clean_title(self, title):
        """
        Extract movie title from RottenTomatoes trailer format.

        Input: "Dune Official Trailer #1 (2025)"
        Output: "Dune"

        Regex logic:
        1. Check if "Trailer #" exists (skip teasers)
        2. Match: ^(.+?)\\s+(?:Official\\s+)?Trailer\\s+#
           - ^(.+?) captures everything before "Trailer"
           - Optional "Official " prefix
           - Mandatory "Trailer #"
        3. Strip whitespace and return

        Returns: Cleaned title or None if not official trailer
        """
```

**Processing Example:**

```
Raw YouTube titles:
- "Dune Official Trailer #1 (2025)" → "Dune"
- "Dune Part Two Official Trailer #2 (2024)" → "Dune Part Two"
- "Dune Teaser Trailer" → None (skipped - no "Trailer #")
- "Dune Behind-the-Scenes" → None (skipped - no "Trailer #")

Data saved to database:
{
    'title': 'Dune',
    'original_title': 'Dune Official Trailer #1 (2025)',
    'year': 2025,
    'video_id': 'xyz123',
    'source': 'rotten_tomatoes'
}
```

### MubiClient - MUBI Channel

```python
class MubiClient(YouTubeBaseClient):
    """
    Mubi channel client.
    Handles Mubi-specific title format: "MOVIE TITLE | Official Trailer #1 | ..."
    Skips teasers and "Coming Soon" announcements.
    """

    CHANNEL_URL = "https://www.youtube.com/@mubi/videos"
    CHANNEL_ID = "UCb6-VM5UQ4Czj_d3m9EPGfg"  # Fallback

    def _clean_title(self, title):
        """
        Extract movie title from MUBI title format.

        Input: "Dune | Official Trailer #1 | Mubi"
        Output: "Dune"

        Logic:
        1. Check if "Official Teaser" or "Coming Soon" exists → skip
        2. Check if "Official Trailer" exists → required
        3. Regex: ^(.+?)\\s*\\|\\s*Official Trailer
           - ^(.+?) captures everything before first pipe
           - \\s*\\|\\s* matches the pipe separator
           - "Official Trailer" must follow
        4. Strip whitespace and return

        Returns: Cleaned title or None if invalid format
        """
```

**Processing Example:**

```
Raw YouTube titles:
- "Dune | Official Trailer #1 | Mubi" → "Dune"
- "THE BRUTALIST | Official Trailer #1 | Mubi" → "THE BRUTALIST"
- "Dune | Official Teaser | Mubi" → None (skipped)
- "Coming Soon | Film Title" → None (skipped)

Data saved to database:
{
    'title': 'Dune',
    'original_title': 'Dune | Official Trailer #1 | Mubi',
    'year': None,  # MUBI format doesn't include year
    'video_id': 'abc456',
    'source': 'mubi'
}
```

**Key Differences Between Clients:**

| Aspect | RottenTomatoes | MUBI |
|--------|---|---|
| URL format | `@ChannelName/videos` | `@channelname/videos` |
| Title format | `Title Official Trailer #1 (2025)` | `TITLE \| Official Trailer #1` |
| Year extraction | Yes (in parentheses) | No |
| Skips | Teasers (no Trailer #) | Teasers, Coming Soon |
| Delimiter | Space | Pipe (`\|`) |

---

## `tmdb/api.py` - TMDB Client for Movie Metadata

**Purpose:** Fetch movie metadata from TMDB API.

### TMDBClient Class

```python
class TMDBClient(BaseClient):
    """
    TMDB (The Movie Database) API client.
    Fetches movie information from TMDB API v3.
    """

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key=None):
        """Initialize with TMDB API key from environment or parameter."""
        self.api_key = api_key or config('TMDB_API_KEY', default=None)
        super().__init__()

    def _validate_config(self):
        """Validate TMDB API key is present."""
        if not self.api_key:
            raise ValidationError(
                "TMDB API key is required. Set TMDB_API_KEY environment variable."
            )

    def _make_request(self, endpoint, params=None):
        """
        Make authenticated request to TMDB API.

        Args:
            endpoint: API endpoint (e.g., '/search/movie')
            params: Query parameters dict

        Process:
        1. Add API key to params
        2. Build full URL: BASE_URL + endpoint
        3. Make GET request with 10s timeout
        4. Check response status (raise_for_status)
        5. Parse and return JSON

        Returns: Response JSON dict
        Raises: NetworkError on HTTP errors, timeouts, connection issues
        """

    def search_movie(self, title, year=None):
        """
        Search TMDB for a movie by title.

        Args:
            title: Movie title (e.g., "Dune")
            year: Optional release year to narrow search

        Process:
        1. Build search params:
           - query: title
           - year: optional
           - include_adult: False (exclude adult content)
        2. Call /search/movie endpoint
        3. If results exist:
           - Take first result (most relevant)
           - Fetch IMDb ID via separate API call
           - Add imdb_id to result dict
           - Return movie dict
        4. If no results: return None

        Returns: Movie dict with:
            - id: TMDB ID
            - title: Movie title
            - release_date: YYYY-MM-DD
            - overview: Plot summary
            - poster_path: Poster URL path
            - backdrop_path: Backdrop URL path
            - imdb_id: IMDb ID (from separate call)
        Returns: None if not found
        """

    def _get_imdb_id(self, tmdb_id):
        """
        Fetch IMDb ID for a TMDB movie.

        Args:
            tmdb_id: TMDB movie ID

        Process:
        1. Call /movie/{tmdb_id}/external_ids endpoint
        2. Extract imdb_id from response
        3. If network error: log warning and return None (graceful failure)

        Returns: IMDb ID string or None
        """

    def get_data(self, **kwargs):
        """
        Generic interface implementing BaseClient.get_data().

        Args:
            **kwargs: Can specify title, query, year parameters

        Returns: Movie dict (delegates to search_movie)
        """
```

**Data Flow:**

```
search_movie("Dune") called
  ├─ Make request to /search/movie?query=Dune&include_adult=False
  ├─ API returns: {results: [{id: 438631, title: "Dune", release_date: "2021-10-22", ...}, ...]}
  ├─ Take first result (most relevant)
  ├─ Call _get_imdb_id(438631)
  │  └─ Make request to /movie/438631/external_ids
  │     └─ API returns: {imdb_id: "tt0319640"}
  ├─ Add imdb_id to movie dict
  └─ Return: {id: 438631, title: "Dune", imdb_id: "tt0319640", overview: "...", ...}
```

**API Response Example:**

```python
# search_movie("Dune") returns:
{
    'id': 438631,                          # TMDB ID
    'title': 'Dune',                       # Movie title
    'release_date': '2021-10-22',         # Release date
    'overview': 'Paul Atreides...',       # Plot summary
    'poster_path': '/68qqQKr3qzqyuAVwCqr4cLmEDUC.jpg',  # Relative poster URL
    'backdrop_path': '/stKGLoCMb3h0KD82EKO0sI2SpG5.jpg', # Relative backdrop URL
    'imdb_id': 'tt0319640'                # IMDb ID (from _get_imdb_id)
}
```

**Error Handling:**

- `ValidationError`: Missing API key
- `NetworkError`: HTTP errors, timeouts, JSON parsing failures
- `NotFoundError`: Could use this for explicit "not found" handling (currently returns None)

---

## `utils/rate_limiter.py` - Rate Limiting

**Purpose:** Prevent API rate limit errors by throttling requests.

```python
class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.

    Ensures maximum number of calls per second to external APIs.
    """

    def __init__(self, calls_per_second=1):
        """
        Args:
            calls_per_second: Max calls/sec (e.g., 4 = 4 calls per second)

        Calculates:
            min_interval = 1.0 / calls_per_second
            Example: 4 calls/sec → min_interval = 0.25 seconds
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_called = 0.0

    def wait_if_needed(self):
        """
        Wait if necessary to maintain rate limit.

        Logic:
        1. Get current time
        2. Calculate time since last call
        3. If time_since_last_call < min_interval:
           - Calculate sleep_time needed
           - Sleep for that duration
        4. Record current time as last_called
        """

    def __call__(self, func):
        """Use as decorator to rate-limit a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
```

**Example Usage:**

```python
# Rate limit to 4 API calls per second
limiter = RateLimiter(calls_per_second=4)

@limiter
def fetch_movie(title):
    return client.search_movie(title)

# First call: executes immediately
fetch_movie("Dune")          # 0ms

# Second call: may wait ~250ms if called immediately
fetch_movie("Blade Runner")  # Waits until 250ms elapsed

# Third call: may wait ~250ms
fetch_movie("Matrix")        # Waits until 500ms elapsed total
```

**Algorithm:**

```
Call 1: time=0ms   ✓ execute immediately
                   └─ min_interval = 250ms

Call 2: time=100ms → need to wait 150ms more → sleep 150ms → execute at 250ms

Call 3: time=300ms → need to wait 200ms more → sleep 200ms → execute at 500ms
```

---

## `utils/decorators.py` - Retry and Caching Decorators

### @retry Decorator - Exponential Backoff

```python
@retry(max_attempts=3, delay=1, backoff=2)
def fetch_data():
    # Code that might fail
    pass
```

**How It Works:**

1. **Attempt 1**: Execute immediately
   - If succeeds: return result
   - If fails: wait `delay` seconds, then retry

2. **Attempt 2**: After waiting `delay` seconds (1s)
   - If succeeds: return result
   - If fails: wait `delay * backoff` seconds (2s), then retry

3. **Attempt 3**: After waiting `delay * backoff` seconds (2s)
   - If succeeds: return result
   - If fails: raise exception

**Example Timeline:**

```
Time 0s:    Attempt 1 fails
            → Wait 1 second

Time 1s:    Attempt 2 fails
            → Wait 2 seconds (1 * 2)

Time 3s:    Attempt 3 fails
            → Raise exception

Total: 3 seconds of waiting across 3 attempts
```

**Exponential Backoff Benefits:**

- First attempt is fast (no waiting)
- Each retry waits longer (prevents thundering herd)
- With backoff=2: 1s, 2s, 4s, 8s, etc.
- Good for transient network errors

### @cached Decorator - In-Memory Caching

```python
@cached(ttl=3600)  # Cache for 1 hour
def get_expensive_data():
    # Expensive computation
    pass
```

**How It Works:**

1. **Cache Key**: Tuple of function args and kwargs
   - `get_expensive_data()` → cache key = `((), ())`
   - `get_movie("Dune")` → cache key = `(("Dune",), ())`

2. **On First Call**:
   - Compute result
   - Store in `cache[key]` and record time
   - Return result

3. **On Subsequent Calls**:
   - If key in cache and not expired (< ttl seconds): return cached result
   - If key not in cache or expired: recompute and update cache

**Example:**

```python
@cached(ttl=3600)  # 1 hour cache
def search_tmdb(title):
    return client.search_movie(title)

search_tmdb("Dune")       # API call, caches result
search_tmdb("Dune")       # Returns cached result (instant)
# After 3600 seconds:
search_tmdb("Dune")       # Cache expired, new API call
```

**Limitations:**

- Single-threaded (not thread-safe)
- In-memory only (lost on process restart)
- Unbounded cache growth (no LRU eviction)

---

## `utils/helpers.py` - Network Helper Functions

### safe_request - HTTP Request with Error Handling

```python
def safe_request(url, method='GET', timeout=10, **kwargs):
    """
    Make a safe HTTP request with error handling.

    Args:
        url: URL to request
        method: HTTP method (GET, POST, PUT, DELETE)
        timeout: Request timeout in seconds
        **kwargs: Additional args for requests library

    Process:
    1. Make HTTP request with timeout
    2. Check status code (raise_for_status)
    3. Return response object

    Raises: NetworkError on any requests.exceptions.RequestException
    """
```

**Example:**

```python
try:
    response = safe_request('https://api.example.com/data')
    data = parse_json_safe(response)
except NetworkError as e:
    print(f"Failed: {e}")
```

### parse_json_safe - JSON Parsing with Error Handling

```python
def parse_json_safe(response):
    """
    Safely parse JSON from response.

    Args:
        response: requests.Response object

    Returns: Parsed JSON dict
    Raises: NetworkError if JSON parsing fails
    """
```

**Example:**

```python
response = safe_request(url)
try:
    data = parse_json_safe(response)
except NetworkError as e:
    print(f"Invalid JSON: {e}")
```

---

## Client Usage in Movies App

### How YouTube Client is Used

In `movies/tasks.py`:

```python
from contrib.youtube import RottenTomatoesClient, MubiClient

# Fetch RottenTomatoes videos
client = RottenTomatoesClient()
videos = client.get_videos()  # Returns list of dicts

# Each dict has:
for video in videos:
    print(video['title'])           # Cleaned title
    print(video['original_title'])  # Raw YouTube title
    print(video['video_id'])        # YouTube ID
    print(video['year'])            # Extracted year (or None)

# Save to database
Movie.objects.create(
    title=video['title'],
    original_title=video['original_title'],
    video_id=video['video_id'],
    source='rotten_tomatoes'
)
```

### How TMDB Client is Used

In `movies/tasks.py`:

```python
from contrib.tmdb import TMDBClient

# Search for movie metadata
client = TMDBClient()
tmdb_data = client.search_movie("Dune")

# tmdb_data contains:
# {
#     'id': 438631,
#     'title': 'Dune',
#     'imdb_id': 'tt0319640',
#     'overview': '...',
#     'release_date': '2021-10-22',
#     'poster_path': '/...',
#     'backdrop_path': '/...'
# }

# Update movie with TMDB data
movie.tmdb_id = tmdb_data['id']
movie.imdb_id = tmdb_data['imdb_id']
movie.overview = tmdb_data['overview']
movie.release_date = tmdb_data['release_date']
movie.poster_path = tmdb_data['poster_path']
movie.backdrop_path = tmdb_data['backdrop_path']
movie.save()
```

---

## Error Handling Pattern

**Standard pattern across all clients:**

```python
try:
    # Validate configuration
    client = SomeClient()

    # Try to fetch data
    data = client.get_data()

except ValidationError as e:
    # Configuration issue - don't retry
    logger.error(f"Config error: {e}")
    raise  # Fail fast

except NetworkError as e:
    # Transient network issue - retry
    logger.error(f"Network error: {e}")
    raise  # Dramatiq will retry

except RateLimitError as e:
    # Rate limited - wait and retry
    logger.warning(f"Rate limited: {e}")
    raise  # Dramatiq will retry with backoff
```

---

## Environment Configuration

**Required environment variables:**

```bash
# TMDB API
TMDB_API_KEY=your_tmdb_api_key_here

# Dramatiq (for task retries)
DRAMATIQ_REDIS_URL=redis://localhost:6379
```

**Optional:**

```bash
# Logging
LOG_LEVEL=INFO
```

---

## Testing

Each client has a test suite:

```
contrib/youtube/tests/
├── conftest.py                    # Fixtures and mocks
├── test_rotten_tomatoes_client.py # RottenTomatoesClient tests
├── test_mubi_client.py            # MubiClient tests
└── test_youtube_integration.py    # Integration tests

contrib/tmdb/tests/
├── conftest.py                    # Fixtures and mocks
└── test_tmdb_client.py            # TMDBClient tests
```

**Key test patterns:**

1. **Mock yt-dlp responses** - Avoid real YouTube API calls
2. **Mock HTTP responses** - Avoid real TMDB API calls
3. **Test title cleaning** - Each client's `_clean_title()` method
4. **Test error handling** - ValidationError, NetworkError, etc.
5. **Test integration** - Full flow from fetch to database save

---

## Summary

The `contrib` package provides:

- **Abstraction**: BaseClient base class for consistent interface
- **YouTube Integration**: RottenTomatoesClient and MubiClient for channel fetching
- **TMDB Integration**: TMDBClient for movie metadata enrichment
- **Utilities**: Rate limiting, retries, caching, error handling
- **Error Handling**: Specific exceptions for different failure modes
- **Testing**: Comprehensive test suite with mocking

All clients follow the same pattern:
1. Configuration validation on initialization
2. Safe HTTP requests with error handling
3. Data parsing and transformation
4. Clear return values or exceptions
