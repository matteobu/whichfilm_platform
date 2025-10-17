from django.shortcuts import render

def film_list(request):
    # For now, just a static list
    films = [
        {"title": "Inception", "year": 2010},
        {"title": "The Matrix", "year": 1999},
        {"title": "Interstellar", "year": 2014},
    ]
    return render(request, "films/film_list.html", {"films": films})