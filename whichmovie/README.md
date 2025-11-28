# WhichMovie Project - Django Configuration and Entry Points

The core Django project configuration for the WhichMovie application.

---

## Overview

`whichmovie` is the **Django project** that:
1. Configures global Django settings (database, installed apps, middleware)
2. Sets up the URL routing structure
3. Initializes the WSGI application for deployment
4. Provides the home view and routing logic

Think of it as the "skeleton" that all Django apps (like `movies`) plug into.

---

## Project Structure

```
whichmovie/
├── __init__.py          # Package initialization
├── settings.py          # Django configuration (database, apps, middleware)
├── urls.py              # Global URL routing
├── views.py             # Project-level views (home page)
├── wsgi.py              # WSGI application entry point (production)
├── asgi.py              # ASGI application entry point (async)
└── README.md            # This file
```

---

## `settings.py` - Django Configuration

**Purpose:** Configure all Django settings for the project.

### Core Settings

```python
# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('DJANGO_SECRET_KEY')    # From environment variable
DEBUG = True                                 # ⚠️ Set to False in production
ALLOWED_HOSTS = []                          # ⚠️ Set to specific hosts in production
```

**Important Notes:**

- `SECRET_KEY`: Loaded from `.env` file (for local development)
- `DEBUG`: Enables verbose error pages (reveals sensitive info, use only in dev)
- `ALLOWED_HOSTS`: Should be `['yourdomain.com']` in production

### Installed Apps

```python
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',         # Admin interface
    'django.contrib.auth',          # User authentication
    'django.contrib.contenttypes',  # Database models
    'django.contrib.sessions',      # Session management
    'django.contrib.messages',      # User messages
    'django.contrib.staticfiles',   # CSS, JS, images

    # Third-party apps
    'django_dramatiq',              # Dramatiq task queue integration
    'dramatiq_crontab',             # Cron scheduling for tasks
    'rest_framework',               # REST API framework

    # Project apps
    'movies',                       # Movie data management
]
```

**What Each App Does:**

| App | Purpose |
|-----|---------|
| `django.contrib.admin` | `/admin/` interface for managing data |
| `django.contrib.auth` | User login, permissions |
| `django.contrib.sessions` | Remember user across requests |
| `django.contrib.messages` | Flash messages ("Success!", "Error!") |
| `django_dramatiq` | Async task queue (background jobs) |
| `dramatiq_crontab` | Schedule tasks on a cron schedule |
| `rest_framework` | Build REST APIs (optional, installed but not used yet) |
| `movies` | The actual WhichMovie functionality |

### Middleware

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",        # Security headers
    "django.contrib.sessions.middleware.SessionMiddleware", # Session handling
    "django.middleware.common.CommonMiddleware",            # CSRF, headers
    "django.middleware.csrf.CsrfViewMiddleware",           # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware", # User auth
    "django.contrib.messages.middleware.MessageMiddleware", # Messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # Clickjacking protection
]
```

**Processing Order:**

Request comes in → SecurityMiddleware → SessionMiddleware → ... → CSRF → ... → Your View

Response goes back through each middleware in reverse order

### URL Configuration

```python
ROOT_URLCONF = "whichmovie.urls"
```

Points Django to the main URL routing file.

### Template Configuration

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],                                    # No custom template dirs
        "APP_DIRS": True,                             # Look in app/templates/
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

**How Django Finds Templates:**

1. `APP_DIRS: True` means Django looks in each app's `templates/` folder
2. For `movies` app: `/movies/templates/movies/movie_list.html`
3. Context processors add data to every template (user, messages, etc.)

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database
        'NAME': config('DB_NAME'),                  # Database name
        'USER': config('DB_USER'),                  # Database user
        'PASSWORD': config('DB_PASSWORD'),          # Database password
        'HOST': config('DB_HOST'),                  # Database host
        'PORT': config('DB_PORT'),                  # Database port
    }
}
```

**Connection Details Loaded from Environment:**

```bash
# .env file
DB_NAME=whichmovie_db
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
```

**Why PostgreSQL?**

- Better than SQLite for production (concurrent writes)
- Better than MySQL for this use case (better JSON support, arrays)
- Open source and free
- Good Django support

### Authentication Configuration

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
```

**What These Validators Do:**

1. **UserAttributeSimilarity**: Don't allow passwords same as username/email
2. **MinimumLength**: Minimum 8 characters (Django default)
3. **CommonPassword**: Block "password123", "qwerty", etc.
4. **NumericPassword**: Block all-numeric passwords

### Localization Settings

```python
LANGUAGE_CODE = "en-us"      # English (US)
TIME_ZONE = "UTC"             # Coordinated Universal Time
USE_I18N = True               # Internationalization (translations)
USE_TZ = True                 # Timezone awareness
```

### Static Files Configuration

```python
STATIC_URL = "static/"
```

**What Are Static Files?**

- CSS stylesheets
- JavaScript files
- Images
- Fonts
- Other non-generated content

**In Development:**

Django serves these automatically from `app/static/` folders

**In Production:**

Run `python manage.py collectstatic` to gather all static files into a single directory, then serve via web server (Nginx, Apache)

### Default Primary Key

```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

All new models get a `BigAutoField` (64-bit integer) for primary keys instead of 32-bit.

### Dramatiq Configuration (Task Queue)

```python
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",  # Use Redis as message broker
    "OPTIONS": {
        "url": config('DRAMATIQ_REDIS_URL', 'redis://localhost:6379'),
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.Retries",    # Enable retry logic
        "dramatiq.middleware.Callbacks",  # Enable callback hooks
    ],
}
```

**How This Works:**

1. **Redis Broker**: Dramatiq stores tasks in Redis queue
2. **Retries Middleware**: Failed tasks are retried automatically
3. **Callbacks Middleware**: Tasks can trigger other tasks when done

**Task Flow:**

```
Movie task scheduled
  ├─ Serialized and stored in Redis
  ├─ Dramatiq worker picks it up
  ├─ Executes the task
  ├─ If fails: Retries middleware retries
  └─ If succeeds: Callbacks middleware runs any dependent tasks
```

---

## `urls.py` - Global URL Routing

**Purpose:** Define the URL structure for the entire project.

```python
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin interface
    path('', views.home, name='home'),         # Home page (landing page)
    path('movies/', include('movies.urls')),   # Movies app URLs
]
```

### URL Mapping

| Path | View | Name | Purpose |
|------|------|------|---------|
| `/admin/` | Django admin | - | Manage database records |
| `/` | `views.home` | `home` | Home page (redirects to movies) |
| `/movies/` | `movies.urls` | - | Include all movies app URLs |

### How Django Matches URLs

**Request comes in:** `GET /movies/`

1. Django checks `urlpatterns` in order
2. Matches `/movies/` against `path('movies/', include('movies.urls'))`
3. Strips matched prefix `/movies/`
4. Passes remaining path to `movies.urls`
5. In `movies/urls.py`: matches empty path `''` to `movie_list`
6. Calls `movie_list(request)` view
7. Returns HTML response

### URL Naming

URLs have names for template references:

```html
<!-- In template -->
<a href="{% url 'home' %}">Home</a>
<a href="{% url 'movie_list' %}">Movies</a>

<!-- Renders as -->
<a href="/">Home</a>
<a href="/movies/">Movies</a>
```

**Benefits of Naming:**

- If you change URL structure, templates still work
- No hardcoded URLs in templates
- Centralized URL management

---

## `views.py` - Project-Level Views

**Purpose:** Provide views for project-level URLs.

```python
from django.shortcuts import redirect

def home(request):
    """Redirect home to movies list."""
    return redirect('movie_list')
```

### What It Does

1. User visits: `GET /`
2. `home()` view is called
3. Returns HTTP redirect (302 status) to `/movies/`
4. Browser follows redirect and loads movie list

**Why Redirect Instead of Showing Content?**

- Home page would just be a list of movies
- More efficient to redirect than duplicate logic
- User ends up at `/movies/` which is more clear

**HTTP Response:**

```
HTTP/1.1 302 Found
Location: /movies/
```

---

## `wsgi.py` - Production Application Entry Point

**Purpose:** Provide the WSGI callable for production web servers.

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whichmovie.settings")
application = get_wsgi_application()
```

### What WSGI Is

**WSGI = Web Server Gateway Interface**

A standard Python interface that web servers use to talk to Python applications.

**How It Works:**

1. Web server (Nginx, Apache) receives HTTP request
2. Passes request to WSGI application
3. WSGI application (Django) processes request
4. Returns HTTP response
5. Web server sends response to client

**Deployment Flow:**

```
Client (Browser)
    ↓
Nginx/Apache (Web Server)
    ↓
gunicorn/uWSGI (WSGI Server)
    ↓
whichmovie.wsgi.application (Django)
    ↓
movies.views.movie_list (Your View)
    ↓
Database
```

### Usage in Production

```bash
# Run with gunicorn (production WSGI server)
gunicorn whichmovie.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

## `asgi.py` - Async Application Entry Point

**Purpose:** Provide the ASGI callable for async web servers (WebSockets, async views).

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whichmovie.settings")
application = get_asgi_application()
```

### ASGI vs WSGI

| Aspect | WSGI | ASGI |
|--------|------|------|
| Async Support | No | Yes |
| WebSockets | No | Yes |
| Performance | Good | Better for I/O |
| Server Examples | gunicorn, uWSGI | Uvicorn, Daphne |

**Current Status:** ASGI is configured but not used (app doesn't have async views or WebSockets yet)

### When to Use ASGI

- Real-time notifications (WebSockets)
- Server-sent events (SSE)
- Async views with `async def`

---

## Configuration for Different Environments

### Development (`DEBUG=True`)

```bash
# .env (development)
DEBUG=True
DJANGO_SECRET_KEY=dev-secret-key-123
DB_NAME=whichmovie_dev
DB_HOST=localhost
DRAMATIQ_REDIS_URL=redis://localhost:6379
```

**Characteristics:**
- Verbose error pages with traceback
- Static files served by Django
- All emails printed to console
- Reloads code on changes

### Production (`DEBUG=False`)

```bash
# Environment variables (production)
DEBUG=False
DJANGO_SECRET_KEY=<generate-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=whichmovie_prod
DB_HOST=prod-db-server
DB_PORT=5432
DRAMATIQ_REDIS_URL=redis://prod-redis-server:6379
```

**Checklist:**
- [ ] Set `DEBUG=False`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use strong `SECRET_KEY` (generate: `django-admin shell` → `from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())`)
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Use HTTPS only
- [ ] Store secrets in environment variables
- [ ] Run `python manage.py collectstatic`
- [ ] Use a production WSGI server (gunicorn, uWSGI)
- [ ] Run in front of a web server (Nginx, Apache)

---

## Dependency Chain

### Request Processing

```
Client Request
  ↓
WSGI/ASGI Application (this file)
  ↓
Middleware (security, sessions, auth)
  ↓
URL Router (urls.py)
  ↓
View (views.py or app views)
  ↓
Model (database queries)
  ↓
Template Rendering
  ↓
HTTP Response
```

### Installed Apps Dependency

```
Django Core Apps
  ├─ admin (needs auth, contenttypes)
  ├─ auth (core authentication)
  └─ sessions (needs auth)

Task Queue
  ├─ django_dramatiq (depends on Dramatiq)
  └─ dramatiq_crontab (depends on Dramatiq)

Project Apps
  └─ movies (depends on models, views)
```

---

## Common Configuration Changes

### Adding a New App

1. Create app: `python manage.py startapp myapp`
2. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       'myapp',  # Add here
   ]
   ```
3. Create models in `myapp/models.py`
4. Create migration: `python manage.py makemigrations myapp`
5. Apply migration: `python manage.py migrate`

### Adding a New URL

1. Add to `urlpatterns` in `urls.py`:
   ```python
   path('path/', include('app.urls')),
   ```
2. Or directly:
   ```python
   path('path/', views.view_function, name='view_name'),
   ```

### Changing Database

1. Update `DATABASES` in `settings.py`
2. Update `DB_*` environment variables
3. Run migrations: `python manage.py migrate`

### Adding a Middleware

1. Create middleware class
2. Add to `MIDDLEWARE` list in `settings.py`
3. Order matters (processed in list order)

---

## Environment Variables

**Required (.env file for local development):**

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=whichmovie_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# External APIs
TMDB_API_KEY=your-tmdb-api-key

# Task Queue
DRAMATIQ_REDIS_URL=redis://localhost:6379
```

**Load from .env:**

```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', cast=bool, default=False)
```

---

## Running Django Commands

```bash
# Start development server
python manage.py runserver

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic --noinput

# Run tests
python manage.py test

# Run background worker
python -m dramatiq movies.tasks
```

---

## Summary

The `whichmovie` project provides:

- **Settings**: Global Django configuration (database, apps, middleware, security)
- **URLs**: Routing structure connecting user requests to views
- **Views**: Project-level views (home page redirects)
- **WSGI**: Production application entry point
- **ASGI**: Async application entry point (for future use)

It's the **glue** that holds all the pieces together:
- Django built-in apps (admin, auth, sessions)
- Third-party apps (Dramatiq, REST Framework)
- Project apps (movies, and any future apps)
- Configuration for database, security, static files, etc.

Without this project configuration, individual apps like `movies` wouldn't work.
