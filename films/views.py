from django.shortcuts import render
from .models import Film

def film_list(request):
    films = Film.objects.all()  # get all films from the database
    return render(request, "films/film_list.html", {"films": films})