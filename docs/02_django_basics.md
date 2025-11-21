# 2. Django Basics: Core Concepts

## What is Django?

Django is a **web framework** - a set of tools and patterns for building websites with Python.

Think of it as a blueprint:
- You define the structure (models, views, URLs)
- Django handles the mechanics (database, HTTP, routing)
- You focus on business logic

## The MVT Pattern

Django uses **MVT** (Model-View-Template) architecture - similar to MVC but with a different name.

```
                HTTP Request
                     ↓
         ┌───────────────────────┐
         │   URL Routing         │
         │   (URLs)              │
         └──────────┬────────────┘
                    ↓
         ┌───────────────────────┐
         │   View                │
         │   (Views.py)          │
         │   - Get data          │
         │   - Process request   │
         │   - Pass to template  │
         └──────────┬────────────┘
                    ↓
         ┌───────────────────────┐
         │   Model               │
         │   (Models.py)         │
         │   - Database query    │
         │   - Business logic    │
         └──────────┬────────────┘
                    ↓
         ┌───────────────────────┐
         │   Template            │
         │   (HTML files)        │
         │   - Render HTML       │
         │   - Display data      │
         └──────────┬────────────┘
                    ↓
                HTTP Response
                (HTML page)
```

### Model
- **What:** Python class representing database table
- **File:** `models.py`
- **Responsibility:** Data structure, database operations
- **Example:** `Movie` model with fields like title, release_date

### View
- **What:** Python function/class handling HTTP requests
- **File:** `views.py`
- **Responsibility:** Get data from model, pass to template
- **Example:** `movie_list()` function that queries all movies

### Template
- **What:** HTML file with dynamic content
- **File:** `templates/` folder
- **Responsibility:** Display data to user
- **Example:** Loop through movies and show each one

### URL
- **What:** Mapping from URL to view
- **File:** `urls.py`
- **Responsibility:** Route requests to correct view
- **Example:** `/movies/` → `movie_list` view

## Project Structure

```
whichmovie_app/
│
├── whichmovie/                 ← PROJECT (global settings)
│   ├── settings.py             Configuration (database, apps, middleware)
│   ├── urls.py                 Global URL routing
│   ├── wsgi.py                 Web server interface
│   └── asgi.py                 Async web server interface
│
├── movies/                      ← APP (one feature/module)
│   ├── migrations/             Database schema history
│   ├── models.py               Database models
│   ├── views.py                Request handlers
│   ├── urls.py                 App-level URL routing
│   ├── admin.py                Admin interface config
│   ├── apps.py                 App configuration
│   ├── forms.py                User input forms
│   └── tests.py                Unit tests
│
├── contrib/                     ← REUSABLE COMPONENTS
│   ├── youtube/
│   │   ├── api.py              YouTube clients
│   │   └── tests/
│   ├── tmdb/
│   │   ├── api.py              TMDB client
│   │   └── tests/
│   └── base/
│       └── client.py           Abstract base classes
│
├── templates/                   ← HTML TEMPLATES
│   ├── base.html               Base template (shared layout)
│   ├── movies/
│   │   ├── movie_list.html     Movie list page
│   │   └── movie_detail.html   Movie detail page
│   └── admin/                  Admin templates (Django built-in)
│
├── static/                      ← STATIC FILES (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── manage.py                    ← Django CLI (main entry point)
├── pytest.ini                   Test configuration
└── requirements.txt             Python dependencies
```

## Apps vs Project

### Project
- **whichmovie/** - Global configuration
- **One per application**
- **Settings, main URLs, WSGI**

### App
- **movies/** - Feature module (movies)
- **Many per project**
- **Models, views, templates for that feature**

Think of it like:
```
Project = Restaurant
Apps = Departments (kitchen, dining room, accounting)
```

## Creating a New App

```bash
python manage.py startapp new_app_name
```

This creates:
```
new_app_name/
├── migrations/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── views.py
└── urls.py
```

Then register in `settings.py`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'new_app_name',  # ← Add here
]
```

## Request-Response Cycle

```
1. User visits URL
   └─ http://localhost:8000/movies/

2. Django receives request
   └─ Check whichmovie/urls.py

3. URL routing
   └─ Find matching URL pattern
   └─ "movies/" matches path("movies/", views.movie_list)

4. View executes
   └─ def movie_list(request):
   └─ Query database via Model
   └─ Pass data to template

5. Template renders
   └─ HTML generated with data
   └─ Movie list displayed

6. Response sent
   └─ HTTP 200 OK
   └─ Body: HTML page
```

## Key Django Components

### 1. Settings (whichmovie/settings.py)

```python
DEBUG = True
INSTALLED_APPS = [...]
DATABASES = {...}
MIDDLEWARE = [...]
TEMPLATES = [...]
STATIC_URL = '/static/'
```

Controls everything about the app.

### 2. URLs (whichmovie/urls.py + movies/urls.py)

Global URLs:
```python
# whichmovie/urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),  # ← Include app URLs
]
```

App-level URLs:
```python
# movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:id>/', views.movie_detail, name='movie_detail'),
]
```

### 3. Views (movies/views.py)

```python
from django.shortcuts import render
from .models import Movie

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

def movie_detail(request, id):
    movie = Movie.objects.get(id=id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})
```

### 4. Models (movies/models.py)

```python
from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()

    def __str__(self):
        return self.title
```

### 5. Templates (templates/movies/movie_list.html)

```html
<h1>Movies</h1>
{% for movie in movies %}
    <div>
        <h2>{{ movie.title }}</h2>
        <p>Released: {{ movie.release_date|date:"Y" }}</p>
    </div>
{% endfor %}
```

## The Three Layers

```
┌─────────────────────────────────────┐
│         PRESENTATION                │ ← What user sees
│      (Templates & Static)           │   HTML, CSS, JS
├─────────────────────────────────────┤
│         BUSINESS LOGIC              │ ← What happens
│        (Views & Models)             │   Process requests, query data
├─────────────────────────────────────┤
│         DATA LAYER                  │ ← Where data lives
│      (Models & Database)            │   PostgreSQL database
└─────────────────────────────────────┘
```

## Django ORM (Object-Relational Mapping)

Django translates Python code to SQL automatically:

```python
# Python (you write this)
movies = Movie.objects.filter(source='rotten_tomatoes')

# SQL (Django generates this)
SELECT * FROM movies_movie WHERE source = 'rotten_tomatoes'
```

You don't write raw SQL (usually). Django handles database queries.

## Middleware Pipeline

Requests pass through middleware layers:

```
Request arrives
    ↓
SecurityMiddleware       ← Check HTTPS, set headers
    ↓
SessionMiddleware        ← Load session
    ↓
AuthenticationMiddleware ← Load user
    ↓
(Your view code runs)
    ↓
AuthenticationMiddleware ← Finalize auth (outbound)
    ↓
SessionMiddleware        ← Save session (outbound)
    ↓
SecurityMiddleware       ← Add headers (outbound)
    ↓
Response sent
```

Middleware can:
- Modify requests before views
- Modify responses after views
- Short-circuit (send response without view)

## Key Concepts Summary

| Concept | Purpose | File |
|---------|---------|------|
| Model | Database schema & queries | models.py |
| View | Handle requests, get data | views.py |
| Template | Display HTML | templates/ |
| URL | Route requests to views | urls.py |
| Form | Handle user input | forms.py |
| Admin | Manage data in browser | admin.py |
| Middleware | Process requests/responses | settings.py |
| Settings | Configuration | settings.py |

## Installation & Setup

```bash
# Install Django
pip install django

# Create project
django-admin startproject whichmovie

# Create app
python manage.py startapp movies

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Common Django Commands

```bash
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Detect model changes
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Python shell with Django
python manage.py test               # Run tests
python manage.py collectstatic      # Collect static files
```

---

Next: [Entry Point](./03_entry_point.md)
