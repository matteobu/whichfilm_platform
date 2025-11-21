# 3. Entry Point: What Happens When You Run `python manage.py runserver`

## The Command Explained

When you type:
```bash
python manage.py runserver
```

You're telling Django to:
1. Start the development server
2. Listen for HTTP requests
3. Process them and return responses

## Step-by-Step Flow

### Step 1: Command Execution

```bash
python manage.py runserver
         ↓
   Django manages
         ↓
   Loads settings
         ↓
   Starts development server
         ↓
   Listens on http://127.0.0.1:8000/
```

### Step 2: Server Initialization

```python
# manage.py executes this
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver"])
```

This triggers:
1. Load Django
2. Read settings from `whichmovie/settings.py`
3. Initialize all installed apps
4. Load all models
5. Start the Werkzeug development server

### Step 3: User Makes a Request

User visits: `http://127.0.0.1:8000/movies/`

```
Request arrives → HTTP GET /movies/
         ↓
   Django receives
         ↓
   Passes to middleware pipeline
         ↓
   Routes to view
         ↓
   View queries database
         ↓
   View renders template
         ↓
   Response sent back to browser
```

## Complete Request-Response Cycle

```
┌─────────────────────────────────────────────────────────────┐
│              1. USER SENDS REQUEST                          │
│                                                             │
│  Browser: GET http://127.0.0.1:8000/movies/                 │
│  Headers: Host, User-Agent, etc.                            │
│  Body: (empty for GET)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         2. DJANGO MIDDLEWARE PIPELINE (IN)                  │
│                                                             │
│  SecurityMiddleware       ← Check HTTPS, set headers        │
│         ↓                                                   │
│  SessionMiddleware        ← Load user session               │
│         ↓                                                   │
│  AuthenticationMiddleware ← Load user object                │
│         ↓                                                   │
│  (Other middleware...)                                      │
│         ↓                                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            3. URL ROUTING                                   │
│                                                             │
│  Check whichmovie/urls.py:                                  │
│    if path == "movies/":                                    │
│        route to: movies.views.movie_list                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            4. VIEW EXECUTION                                │
│                                                             │
│  def movie_list(request):                                   │
│    movies = Movie.objects.all()    ← Query database         │
│    return render(...)              ← Render template        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         5. TEMPLATE RENDERING                               │
│                                                             │
│  movies/movie_list.html                                     │
│    ↓                                                        │
│  Loop through {{ movies }}                                  │
│    ↓                                                        │
│  Generate HTML                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│      6. DJANGO MIDDLEWARE PIPELINE (OUT)                    │
│                                                             │
│  AuthenticationMiddleware ← Finalize auth                   │
│         ↓                                                   │
│  SessionMiddleware        ← Save session                    │
│         ↓                                                   │
│  SecurityMiddleware       ← Add security headers            │
│         ↓                                                   │
│  (Other middleware...)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         7. RESPONSE SENT TO BROWSER                         │
│                                                             │
│  HTTP 200 OK                                                │
│  Headers: Content-Type, Set-Cookie, etc.                    │
│  Body: HTML content (movie list)                            │
└─────────────────────────────────────────────────────────────┘
```

## File Execution Order

When you run `python manage.py runserver`, Django loads files in this order:

### 1. **manage.py**
```python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whichmovie.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```

Sets environment variable and calls Django CLI.

### 2. **whichmovie/settings.py**
```python
DEBUG = True
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'movies',          # ← Our app
    'contrib.youtube', # ← Our component
    'contrib.tmdb',    # ← Our component
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        ...
    }
}
```

Loads configuration (debug mode, apps, database, middleware, etc.)

### 3. **whichmovie/wsgi.py**
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whichmovie.settings")
application = get_wsgi_application()
```

Creates the WSGI application object (interface between web server and Django).

### 4. **whichmovie/urls.py**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("movies.urls")),
]
```

Loads URL configuration (routing rules).

### 5. **movies/urls.py**
```python
from django.urls import path
from . import views

urlpatterns = [
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
]
```

App-level URL configuration.

### 6. **movies/apps.py**
```python
from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
```

App configuration (registered in INSTALLED_APPS).

### 7. **movies/models.py**
```python
from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    ...
```

Model definitions (database schema).

## What Happens at Different URLs

### Request: GET `/movies/`

```
URL: /movies/

1. Router finds in movies/urls.py:
   path("movies/", views.movie_list)

2. Executes view:
   def movie_list(request):
       movies = Movie.objects.all()
       return render(request, 'movies/movie_list.html', {'movies': movies})

3. Executes query:
   SELECT * FROM movies_movie

4. Gets 42 movies from database

5. Renders template:
   movies/movie_list.html (loops through 42 movies)

6. Returns HTML response with 42 movies listed
```

### Request: GET `/admin/`

```
URL: /admin/

1. Router finds in whichmovie/urls.py:
   path("admin/", admin.site.urls)

2. Django admin interface loads

3. Shows:
   - Authentication (login page if not logged in)
   - Models (Movie, User, etc.)
   - Data management interface
```

## Server Information

When server starts, you'll see:

```
Django version 5.2.8
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This means:
- Django 5.2.8 is running
- Server is at `http://127.0.0.1:8000/` (localhost:8000)
- Press Ctrl+C to stop

## How Changes Auto-Reload

```
File changes detected:
  - Save models.py

Django detects change:
  - Reloads Python modules
  - Re-imports from settings.py
  - Reloads all apps
  - Reloads URL configuration

Server restarts automatically
(Usually <1 second)
```

This is why development is fast - you don't need to restart manually.

## Debugging the Request

To see what happens at each step, add print statements:

```python
# whichmovie/urls.py
print("URL patterns loaded")

# movies/views.py
def movie_list(request):
    print("movie_list view called")
    print(f"User: {request.user}")
    movies = Movie.objects.all()
    print(f"Found {movies.count()} movies")
    return render(request, 'movies/movie_list.html', {'movies': movies})

# movies/models.py
print("Movie model loaded")
```

When you visit `/movies/`, you'll see:
```
URL patterns loaded
Movie model loaded
movie_list view called
User: AnonymousUser
Found 42 movies
```

---

Next: [URL Routing](./04_url_routing.md)
