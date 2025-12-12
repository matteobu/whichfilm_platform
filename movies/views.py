from django.shortcuts import render

from .models import Movie


def movie_list(request):
    """Display list of all movies with TMDB enrichment data."""
    # Get all movies ordered by creation date (newest first)
    movies = Movie.objects.all().order_by("-created_at")

    context = {
        "movies": movies,
        "total_movies": movies.count(),
        "enriched_movies": movies.filter(tmdb_id__isnull=False).count(),
    }

    return render(request, "movies/movie_list.html", context)
