"""
Tests for TMDBClient.

Organized by method type:
- API tests: search_movie (with mocking)
- Utility tests: _get_imdb_id
- Interface tests: get_data
- Error handling: ValidationError, NetworkError
"""


class TestTMDBClientSearchMovie:
    """Test suite for TMDBClient.search_movie() method."""

    def test_search_movie__finds_movie_by_title(self):
        """
        Test that search_movie finds a movie by title.

        NEEDS:
        - Mock the TMDB API response for "Star Wars"
        - Mock the _make_request method
        - Call search_movie("Star Wars")
        - Verify: Returns dict with id, title, release_date, overview, poster_path, backdrop_path

        EXPECTED DATA:
        {
            'id': 11,
            'title': 'Star Wars',
            'release_date': '1977-05-25',
            'overview': 'A long time ago...',
            'poster_path': '/path/to/poster.jpg',
            'backdrop_path': '/path/to/backdrop.jpg',
            'imdb_id': 'tt0076759'
        }
        """
        pass

    def test_search_movie__finds_movie_with_year_filter(self):
        """
        Test that search_movie narrows results by year.

        NEEDS:
        - Mock TMDB API call with year parameter
        - Call search_movie("Dune", year=2021)
        - Verify: API request includes year in params
        - Verify: Returns correct movie (Dune 2021, not Dune 1984)

        EXPECTED BEHAVIOR:
        - When year is provided, should call API with year filter
        - Should return the 2021 version of Dune
        """
        pass

    def test_search_movie__returns_none_when_not_found(self):
        """
        Test that search_movie returns None when movie not found.

        NEEDS:
        - Mock empty TMDB API response
        - Call search_movie("NonexistentMovieXYZ123")
        - Verify: Returns None

        EXPECTED BEHAVIOR:
        - API returns empty results list
        - Function should return None (not raise error)
        """
        pass

    def test_search_movie__handles_missing_optional_fields(self):
        """
        Test that search_movie handles missing optional fields gracefully.

        NEEDS:
        - Mock TMDB response with missing fields (poster_path=None, backdrop_path=None)
        - Call search_movie("Movie")
        - Verify: Returns data with None values for missing fields

        EXPECTED BEHAVIOR:
        - Should not crash if optional fields are missing
        - Should preserve None values for missing fields
        """
        pass


class TestTMDBClientGetImdbId:
    """Test suite for TMDBClient._get_imdb_id() method."""

    def test_get_imdb_id__fetches_imdb_id_from_tmdb_id(self):
        """
        Test that _get_imdb_id fetches IMDb ID from TMDB ID.

        NEEDS:
        - Mock the external_ids API endpoint
        - Call _get_imdb_id(11)  # TMDB ID for Star Wars
        - Verify: Returns 'tt0076759' (IMDb ID)

        EXPECTED DATA:
        - Calls: /movie/11/external_ids
        - Returns: 'tt0076759'
        """
        pass

    def test_get_imdb_id__returns_none_on_error(self):
        """
        Test that _get_imdb_id returns None gracefully on error.

        NEEDS:
        - Mock API error (NetworkError, etc.)
        - Call _get_imdb_id(invalid_id)
        - Verify: Returns None (not raises exception)
        - Verify: Logs warning

        EXPECTED BEHAVIOR:
        - Should not propagate exceptions
        - Should log warning message
        - Should return None so enrichment can continue
        """
        pass


class TestTMDBClientGetData:
    """Test suite for TMDBClient.get_data() method (implements BaseClient interface)."""

    def test_get_data__searches_and_returns_movie_data(self):
        """
        Test that get_data searches for movie and returns data.

        NEEDS:
        - Call get_data(title="Star Wars")
        - Verify: Calls search_movie internally
        - Verify: Returns movie data dict

        EXPECTED BEHAVIOR:
        - Should accept title parameter
        - Should call search_movie with title
        - Should return result
        """
        pass

    def test_get_data__requires_title_parameter(self):
        """
        Test that get_data raises error when title missing.

        NEEDS:
        - Call get_data() with no parameters
        - Verify: Raises ValidationError
        - Verify: Error message mentions 'title' or 'query' required

        EXPECTED BEHAVIOR:
        - Should validate that title/query is provided
        - Should raise ValidationError
        """
        pass

    def test_get_data__passes_year_to_search(self):
        """
        Test that get_data passes year parameter to search_movie.

        NEEDS:
        - Call get_data(title="Dune", year=2021)
        - Verify: search_movie was called with year=2021

        EXPECTED BEHAVIOR:
        - Should accept optional year parameter
        - Should pass it to search_movie
        """
        pass


class TestTMDBClientValidation:
    """Test suite for TMDBClient configuration validation."""

    def test_init__validates_api_key_configured(self):
        """
        Test that __init__ validates TMDB_API_KEY is set.

        NEEDS:
        - Mock environment with missing TMDB_API_KEY
        - Try to create TMDBClient()
        - Verify: Raises ValidationError

        EXPECTED BEHAVIOR:
        - Should call _validate_config()
        - Should raise ValidationError if TMDB_API_KEY not in env
        """
        pass

    def test_init__accepts_api_key_parameter(self):
        """
        Test that __init__ accepts API key as parameter.

        NEEDS:
        - Create TMDBClient(api_key="test_key_123")
        - Verify: Client is initialized successfully
        - Verify: Uses provided key instead of env var

        EXPECTED BEHAVIOR:
        - Should accept api_key parameter
        - Should use parameter value over env var
        """
        pass

    def test_init__falls_back_to_env_variable(self):
        """
        Test that __init__ falls back to TMDB_API_KEY env var.

        NEEDS:
        - Mock environment with TMDB_API_KEY="env_key_123"
        - Create TMDBClient() without parameter
        - Verify: Uses env var value

        EXPECTED BEHAVIOR:
        - Should read TMDB_API_KEY from environment
        - Should use it if no parameter provided
        """
        pass


class TestTMDBClientNetworkErrors:
    """Test suite for network error handling."""

    def test_search_movie__handles_network_error(self):
        """
        Test that search_movie handles network errors gracefully.

        NEEDS:
        - Mock _make_request to raise NetworkError
        - Call search_movie("Star Wars")
        - Verify: Raises NetworkError
        - Verify: Error message is descriptive

        EXPECTED BEHAVIOR:
        - Should propagate NetworkError (not silent fail)
        - Should provide helpful error message
        """
        pass

    def test_search_movie__handles_timeout(self):
        """
        Test that search_movie handles API timeout.

        NEEDS:
        - Mock _make_request to timeout (10 second timeout)
        - Call search_movie("Star Wars")
        - Verify: Raises NetworkError or appropriate exception

        EXPECTED BEHAVIOR:
        - Should handle timeout gracefully
        - Should log timeout message
        """
        pass
