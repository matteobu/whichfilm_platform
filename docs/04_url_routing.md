# 4. URL Routing: Mapping URLs to Views

## What is URL Routing?

URL routing is the **mapping system** that connects URLs to views.

When user visits a URL, Django:
1. Receives the URL
2. Checks all URL patterns
3. Finds a match
4. Calls the corresponding view function

```
User visits: http://localhost:8000/movies/
         ↓
Django checks: whichmovie/urls.py
         ↓
Found: path('movies/', views.movie_list)
         ↓
Calls: movie_list view function
         ↓
Returns: HTML response
```

## URL Pattern Syntax

### Basic Pattern

```python
from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movie_list, name='movie_list'),
]
```

**Breakdown:**
- `'movies/'` - URL path (what user types)
- `views.movie_list` - View function to call
- `name='movie_list'` - Internal name for this URL (optional but recommended)

### With Parameters

```python
path('movies/<int:id>/', views.movie_detail, name='movie_detail')
```

**Breakdown:**
- `<int:id>` - URL parameter
  - `int` - Type (converts to integer)
  - `id` - Variable name (passed to view)

**Examples:**
- User visits: `/movies/1/` → `id=1`
- User visits: `/movies/42/` → `id=42`
- User visits: `/movies/abc/` → 404 Error (not an integer)

### Parameter Types

```python
# Integer (whole numbers)
path('movies/<int:id>/', views.movie_detail)
# /movies/1/ → id=1
# /movies/999/ → id=999

# String (text)
path('search/<str:query>/', views.search)
# /search/dune/ → query='dune'
# /search/blade runner/ → query='blade runner'

# Slug (text with hyphens/underscores)
path('movies/<slug:slug>/', views.movie_by_slug)
# /movies/the-lord-of-the-rings/ → slug='the-lord-of-the-rings'

# UUID (unique identifiers)
path('movies/<uuid:movie_id>/', views.movie_by_uuid)
# /movies/f47ac10b-58cc-4372-a567-0e02b2c3d479/ → movie_id=f47ac10b-58cc-4372-a567-0e02b2c3d479
```

## Global vs App-Level URLs

### Global URLs (whichmovie/urls.py)

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Include app URLs
    path('', include('movies.urls')),
]
```

This **includes** app-level URLs under a prefix (or empty prefix).

### App-Level URLs (movies/urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:id>/', views.movie_detail, name='movie_detail'),
]
```

These are the **actual routes**.

### How They Combine

```
Global: path('', include('movies.urls'))
App:    path('movies/', views.movie_list)
         ↓
Final URL: /movies/
```

Another example:

```
Global: path('api/', include('api.urls'))
App:    path('movies/', views.get_movies)
         ↓
Final URL: /api/movies/
```

## URL Patterns in This Project

### movies/urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),              # /
    path('movies/', views.movie_list, name='movie_list'),     # /movies/
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),  # /movies/1/
]
```

### Resulting URLs

```
http://localhost:8000/             → home view
http://localhost:8000/movies/      → movie_list view
http://localhost:8000/movies/1/    → movie_detail view (id=1)
http://localhost:8000/movies/42/   → movie_detail view (id=42)
http://localhost:8000/movies/abc/  → 404 Error (not an integer)
```

## View Functions with Parameters

### Without Parameters

```python
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})
```

URL: `path('movies/', views.movie_list)`

No parameters to handle.

### With Parameters

```python
def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)
    return render(request, 'movies/movie_detail.html', {'movie': movie})
```

URL: `path('movies/<int:pk>/', views.movie_detail)`

Parameter `pk` comes from URL and is passed to view.

### Multiple Parameters

```python
def movie_search(request, source, year):
    movies = Movie.objects.filter(
        source=source,
        release_date__year=year
    )
    return render(request, 'movies/search_results.html', {'movies': movies})
```

URL: `path('movies/<str:source>/<int:year>/', views.movie_search)`

- `/movies/rotten_tomatoes/2021/` → source='rotten_tomatoes', year=2021
- `/movies/mubi/2023/` → source='mubi', year=2023

## URL Names (Reverse URLs)

### Why Use URL Names?

Instead of hardcoding URLs in templates, use names:

```html
<!-- BAD: Hardcoded URL -->
<a href="/movies/42/">View Movie</a>

<!-- GOOD: Using name -->
<a href="{% url 'movie_detail' movie.id %}">View Movie</a>
```

If you change the URL pattern, templates automatically work.

### URL Reversing in Views

```python
from django.urls import reverse

# Reverse a URL
url = reverse('movie_detail', args=[42])
# Returns: '/movies/42/'

# Redirect to a named URL
from django.shortcuts import redirect
return redirect('movie_detail', pk=42)
```

### URL Reversing in Templates

```html
<!-- Simple URL -->
<a href="{% url 'movie_list' %}">All Movies</a>
<!-- Generates: <a href="/movies/">All Movies</a> -->

<!-- URL with parameters -->
<a href="{% url 'movie_detail' movie.id %}">{{ movie.title }}</a>
<!-- Generates: <a href="/movies/42/">Dune</a> -->

<!-- URL with named parameters -->
<a href="{% url 'movie_detail' pk=movie.id %}">View</a>
```

## Regular Expressions (Advanced)

For complex patterns, use `re_path` instead of `path`:

```python
from django.urls import re_path

urlpatterns = [
    # Match year (4 digits)
    re_path(r'^movies/(?P<year>\d{4})/$', views.movies_by_year),

    # Match custom slug pattern
    re_path(r'^articles/(?P<slug>[\w-]+)/$', views.article_detail),
]
```

**Examples:**
- `/movies/2021/` → year='2021'
- `/articles/my-article-title/` → slug='my-article-title'

## Query Parameters vs Path Parameters

### Path Parameters (in URL)

```python
# URL pattern
path('movies/<int:id>/', views.movie_detail)

# Usage
/movies/42/  ← id is in the path
```

### Query Parameters (after ?)

```python
# URL pattern (just the base)
path('search/', views.search)

# Usage
/search/?q=dune&year=2021  ← q and year are query parameters
```

**In view:**
```python
def search(request):
    query = request.GET.get('q')     # 'dune'
    year = request.GET.get('year')   # '2021'

    movies = Movie.objects.filter(
        title__icontains=query,
        release_date__year=year
    )
    return render(request, 'search_results.html', {'movies': movies})
```

## URL Namespacing

If multiple apps have same URL names, use namespacing:

```python
# whichmovie/urls.py
urlpatterns = [
    path('movies/', include(('movies.urls', 'movies'), namespace='movies')),
    path('admin/', include(('admin_panel.urls', 'admin_panel'), namespace='admin')),
]
```

Then reference with namespace:

```html
<!-- movies app -->
<a href="{% url 'movies:movie_list' %}">Movies</a>

<!-- admin app -->
<a href="{% url 'admin:dashboard' %}">Dashboard</a>
```

## HTTP Methods (GET, POST, etc)

By default, views accept any HTTP method. Restrict if needed:

```python
from django.views.decorators.http import require_GET, require_POST

# Accept only GET
@require_GET
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

# Accept only POST
@require_POST
def create_movie(request):
    title = request.POST.get('title')
    movie = Movie.objects.create(title=title)
    return redirect('movie_detail', pk=movie.id)
```

## Testing URLs

### Unit Test URLs

```python
from django.test import SimpleTestCase
from django.urls import reverse

class URLTests(SimpleTestCase):
    def test_movie_list_url(self):
        url = reverse('movie_list')
        self.assertEqual(url, '/movies/')

    def test_movie_detail_url(self):
        url = reverse('movie_detail', args=[42])
        self.assertEqual(url, '/movies/42/')
```

### Test Views Respond to URLs

```python
from django.test import Client

def test_movie_list_view():
    client = Client()
    response = client.get('/movies/')
    assert response.status_code == 200
    assert 'movies' in response.context
```

## Common URL Patterns

```python
# List and detail views
path('movies/', views.MovieListView.as_view(), name='movie_list'),
path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),

# Create, update, delete
path('movies/create/', views.MovieCreateView.as_view(), name='movie_create'),
path('movies/<int:pk>/update/', views.MovieUpdateView.as_view(), name='movie_update'),
path('movies/<int:pk>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),

# Search
path('search/', views.search, name='search'),

# API endpoints
path('api/movies/', views.api_movies, name='api_movies'),
```

## 404 Handling

If URL doesn't match any pattern → 404 Not Found

```python
# User visits: /movies/abc/ (not a valid integer)
# No pattern matches
# Django returns: HTTP 404 Not Found

# Custom 404 page
# Create: templates/404.html
# Django automatically uses it when path not found
```

## URL Best Practices

1. **Keep URLs semantic**
   ```python
   # ✅ Good
   path('movies/', views.movie_list)
   path('movies/<int:pk>/', views.movie_detail)

   # ❌ Bad
   path('m/', views.movie_list)
   path('d/<int:id>/', views.movie_detail)
   ```

2. **Always use trailing slashes**
   ```python
   # ✅ Good
   path('movies/', views.movie_list)

   # ❌ Bad
   path('movies', views.movie_list)
   ```

3. **Use URL names**
   ```python
   # ✅ Good
   path('movies/', views.movie_list, name='movie_list')

   # ❌ Bad
   path('movies/', views.movie_list)
   ```

4. **Use appropriate parameter types**
   ```python
   # ✅ Good
   path('movies/<int:pk>/', views.movie_detail)

   # ❌ Bad
   path('movies/<pk>/', views.movie_detail)  # defaults to string
   ```

---

Next: [Views](./05_views.md)
