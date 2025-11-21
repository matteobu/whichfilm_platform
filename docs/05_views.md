# 5. Views: Request Handlers

## What is a View?

A view is a **Python function or class** that handles an HTTP request and returns an HTTP response.

```
Request arrives
    ↓
View function
    ├─ Get data from database (models)
    ├─ Process the request
    └─ Return response (HTML, JSON, redirect)
    ↓
Response sent
```

## Two Types of Views

### 1. Function-Based Views (FBV)

Simple Python functions:

```python
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

- **Simple to understand**
- **Used for basic logic**
- **Common in this project**

### 2. Class-Based Views (CBV)

Classes with methods:

```python
from django.views import View

class MovieListView(View):
    def get(self, request):
        movies = Movie.objects.all()
        return render(request, 'movies/movie_list.html', {'movies': movies})
```

- **More reusable**
- **Better for complex logic**
- **More Django conventions**

## Function-Based Views (Used in This Project)

### Basic Structure

```python
from django.shortcuts import render
from .models import Movie

def movie_list(request):
    # 1. Get data
    movies = Movie.objects.all()

    # 2. Prepare context
    context = {'movies': movies}

    # 3. Render template
    return render(request, 'movies/movie_list.html', context)
```

### The Request Object

Every view receives a **request object** with info about the request:

```python
def my_view(request):
    # HTTP method
    method = request.method  # 'GET', 'POST', 'DELETE', etc.

    # User
    user = request.user  # Anonymous or logged-in user

    # GET parameters (?key=value)
    query = request.GET.get('q')  # From /search/?q=dune

    # POST parameters (form data)
    title = request.POST.get('title')

    # Path parameters (from URL)
    # These come from URL pattern: <int:pk>
    # Passed as function argument

    # Headers
    user_agent = request.META.get('HTTP_USER_AGENT')

    # Full URL
    url = request.get_full_path()  # /movies/?sort=date
```

### Responses

Views must return a response. Common types:

```python
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# 1. HTML Response (template rendering)
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

# 2. Redirect Response
def old_url(request):
    return redirect('movie_list')  # Redirect to another view

# 3. JSON Response (for APIs)
def api_movies(request):
    movies = list(Movie.objects.values('title', 'release_date'))
    return JsonResponse({'movies': movies})

# 4. Plain Text Response
def plain_text(request):
    return HttpResponse("Hello, World!")

# 5. File Download
from django.http import FileResponse
def download_csv(request):
    return FileResponse(open('movies.csv', 'rb'))
```

## Views in This Project

### movies/views.py

```python
from django.shortcuts import render
from .models import Movie

def movie_list(request):
    """Display all movies."""
    movies = Movie.objects.all().order_by('-created_at')

    context = {
        'movies': movies,
        'total_movies': movies.count(),
        'enriched_movies': movies.filter(tmdb_id__isnull=False).count(),
    }

    return render(request, 'movies/movie_list.html', context)


def movie_detail(request, pk):
    """Display a single movie."""
    movie = Movie.objects.get(pk=pk)

    context = {
        'movie': movie,
        'related_movies': Movie.objects.filter(source=movie.source).exclude(pk=pk)[:5],
    }

    return render(request, 'movies/movie_detail.html', context)
```

## Common View Patterns

### 1. List View (Get all items)

```python
def movie_list(request):
    # Get all movies
    movies = Movie.objects.all()

    # Optionally filter
    source = request.GET.get('source')
    if source:
        movies = movies.filter(source=source)

    # Optionally order
    movies = movies.order_by('-created_at')

    # Optionally paginate
    from django.core.paginator import Paginator
    paginator = Paginator(movies, 10)  # 10 per page
    page_number = request.GET.get('page')
    movies = paginator.get_page(page_number)

    return render(request, 'movies/movie_list.html', {'movies': movies})
```

### 2. Detail View (Get one item)

```python
def movie_detail(request, pk):
    # Get specific movie
    movie = Movie.objects.get(pk=pk)

    # Or with error handling
    from django.shortcuts import get_object_or_404
    movie = get_object_or_404(Movie, pk=pk)  # Returns 404 if not found

    return render(request, 'movies/movie_detail.html', {'movie': movie})
```

### 3. Create View (POST form data)

```python
def create_movie(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        source = request.POST.get('source')

        # Create object
        movie = Movie.objects.create(
            title=title,
            source=source
        )

        # Redirect to detail
        return redirect('movie_detail', pk=movie.pk)

    # GET request: show form
    return render(request, 'movies/create_movie.html')
```

### 4. Update View (PUT/POST)

```python
def update_movie(request, pk):
    movie = Movie.objects.get(pk=pk)

    if request.method == 'POST':
        # Update fields
        movie.title = request.POST.get('title', movie.title)
        movie.source = request.POST.get('source', movie.source)
        movie.save()

        return redirect('movie_detail', pk=movie.pk)

    # GET request: show form
    return render(request, 'movies/update_movie.html', {'movie': movie})
```

### 5. Delete View (DELETE/POST)

```python
def delete_movie(request, pk):
    movie = Movie.objects.get(pk=pk)

    if request.method == 'POST':
        movie.delete()
        return redirect('movie_list')

    # GET request: show confirmation
    return render(request, 'movies/delete_movie.html', {'movie': movie})
```

## Filtering and Querying

### Simple Filter

```python
def rotten_tomatoes_movies(request):
    # Get only RottenTomatoes movies
    movies = Movie.objects.filter(source='rotten_tomatoes')
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

### Multiple Filters

```python
def enriched_rotten_movies(request):
    # Get enriched RottenTomatoes movies
    movies = Movie.objects.filter(
        source='rotten_tomatoes',
        tmdb_id__isnull=False  # Has TMDB ID (enriched)
    )
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

### Exclude

```python
def movies_without_plot(request):
    # Get movies without plot summary
    movies = Movie.objects.filter(overview__isnull=True)
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

### Ordering

```python
def latest_movies(request):
    # Get newest movies first
    movies = Movie.objects.all().order_by('-created_at')
    return render(request, 'movies/movie_list.html', {'movies': movies})

def oldest_movies(request):
    # Get oldest movies first
    movies = Movie.objects.all().order_by('created_at')
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

## Status Codes

Views return different HTTP status codes:

```python
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError

# 200 OK (default)
def success_view(request):
    return render(request, 'success.html')

# 201 Created
def create_view(request):
    movie = Movie.objects.create(...)
    return HttpResponse('Created', status=201)

# 301 Moved Permanently (redirect)
def old_view(request):
    return redirect('new_view')  # HTTP 301

# 302 Found (temporary redirect)
def temp_redirect(request):
    return redirect('other_view')  # HTTP 302

# 400 Bad Request
def bad_request(request):
    return HttpResponse('Bad Request', status=400)

# 403 Forbidden
from django.http import HttpResponseForbidden
def admin_only(request):
    if not request.user.is_admin:
        return HttpResponseForbidden('Access denied')

# 404 Not Found (automatic)
from django.shortcuts import get_object_or_404
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)  # Returns 404 if not found

# 500 Internal Server Error (exception)
def error_view(request):
    raise Exception("Something went wrong")  # Returns 500
```

## View Decorators

### Authentication Required

```python
from django.contrib.auth.decorators import login_required

@login_required
def admin_panel(request):
    # Only accessible to logged-in users
    return render(request, 'admin.html')
```

### Permission Required

```python
from django.contrib.auth.decorators import permission_required

@permission_required('movies.change_movie')
def edit_movie(request, pk):
    # Only users with 'change_movie' permission
    movie = Movie.objects.get(pk=pk)
    return render(request, 'edit_movie.html', {'movie': movie})
```

### HTTP Method Restriction

```python
from django.views.decorators.http import require_GET, require_POST

@require_GET
def list_movies(request):
    # Only accepts GET requests
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})

@require_POST
def create_movie(request):
    # Only accepts POST requests
    title = request.POST.get('title')
    movie = Movie.objects.create(title=title)
    return JsonResponse({'id': movie.pk})
```

### Cache Control

```python
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache for 60 seconds
def expensive_view(request):
    # This view's response is cached
    movies = Movie.objects.all()  # Only queried once per 60 seconds
    return render(request, 'movie_list.html', {'movies': movies})
```

## Context (Data Passed to Templates)

```python
def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)

    context = {
        'movie': movie,                    # Single object
        'title': movie.title,              # String
        'count': 42,                       # Number
        'items': [1, 2, 3],                # List
        'dict': {'key': 'value'},          # Dictionary
        'is_enriched': movie.tmdb_id is not None,  # Boolean
    }

    return render(request, 'movies/movie_detail.html', context)
```

In the template:
```html
<h1>{{ movie.title }}</h1>
<p>Title: {{ title }}</p>
<p>Count: {{ count }}</p>
{% if is_enriched %}
    <p>This movie is enriched</p>
{% endif %}
```

## Error Handling

### Try-Except

```python
def movie_detail(request, pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return render(request, '404.html', status=404)

    return render(request, 'movies/movie_detail.html', {'movie': movie})
```

### Get or 404

```python
from django.shortcuts import get_object_or_404

def movie_detail(request, pk):
    # Automatically returns 404 if not found
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movies/movie_detail.html', {'movie': movie})
```

## View Best Practices

1. **Keep views small and focused**
   ```python
   # ✅ Good: One responsibility
   def movie_list(request):
       movies = Movie.objects.all()
       return render(request, 'movies/movie_list.html', {'movies': movies})

   # ❌ Bad: Too much logic
   def dashboard(request):
       movies = Movie.objects.all()
       users = User.objects.all()
       stats = calculate_stats()
       send_emails()
       # ...
   ```

2. **Use get_object_or_404**
   ```python
   # ✅ Good
   movie = get_object_or_404(Movie, pk=pk)

   # ❌ Bad
   try:
       movie = Movie.objects.get(pk=pk)
   except Movie.DoesNotExist:
       raise Http404()
   ```

3. **Use descriptive names**
   ```python
   # ✅ Good
   def movie_list(request):
   def enriched_movies(request):
   def search_movies(request):

   # ❌ Bad
   def list1(request):
   def movies(request):
   def search(request):
   ```

4. **Return appropriate status codes**
   ```python
   # ✅ Good: Explicitly set status
   return HttpResponse('Created', status=201)
   return redirect('movie_list')

   # ❌ Bad: Always returns 200
   return render(request, 'created.html')
   ```

---

Next: [Models](./06_models.md)
