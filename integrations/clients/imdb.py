from django.conf import settings


class IMDbAPIClient:
    """IMDb API client for fetching movie information"""

    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'IMDB_API_KEY', '')
        self.base_url = getattr(settings, 'IMDB_API_BASE_URL', 'https://www.omdbapi.com/')

    def search_movie(self, title, year=None):
        """
        Search for a movie on IMDb.

        Args:
            title (str): Movie title to search
            year (int, optional): Release year

        Returns:
            dict: Movie information including title, year, rating, etc.
                  Returns None if not found
        """
        # TODO: Implement IMDb API search
        pass

    def get_movie_details(self, imdb_id):
        """
        Get full movie details by IMDb ID.

        Args:
            imdb_id (str): IMDb movie ID (e.g., 'tt1234567')

        Returns:
            dict: Complete movie information
        """
        # TODO: Implement IMDb API details fetch
        pass
