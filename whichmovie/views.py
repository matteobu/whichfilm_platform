from django.shortcuts import render, redirect


def home(request):
    """Redirect home to movies list."""
    return redirect('movie_list')
