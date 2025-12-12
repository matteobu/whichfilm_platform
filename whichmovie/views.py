from django.shortcuts import redirect


def home(request):
    """Redirect home to movies list."""
    return redirect("movie_list")
