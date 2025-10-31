from django.shortcuts import render
from .models import Movie

def movie_list(request):
    movies = Movie.objects.all()  # get all movies from the database
    return render(request, "movies/movie_list.html", {"movies": movies})