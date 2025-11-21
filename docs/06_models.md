# 6. Models: Database Layer

## What is a Model?

A Django model is a Python class that represents a **database table**.

Each model:
- Maps to one database table
- Has attributes that map to table columns
- Has methods for database operations (create, read, update, delete)

## How It Works

```
Django Model (Python)
         ↓
   ORM (Object-Relational Mapping)
         ↓
SQL Queries
         ↓
PostgreSQL Database
```

Django translates Python code to SQL automatically. You don't write raw SQL.

### Example

```python
# Django Model (Python)
class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()

# ORM Translation
movie = Movie.objects.create(
    title='Dune',
    release_date='2021-10-22'
)

# Generated SQL
INSERT INTO movies_movie (title, release_date) VALUES ('Dune', '2021-10-22')
```

## The Movie Model in This Project

**Location:** `movies/models.py`

```python
class Movie(models.Model):
    # Core Fields
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True, null=True)

    # External IDs for deduplication
    tmdb_id = models.IntegerField(blank=True, null=True, unique=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    # Source Tracking
    source = models.CharField(max_length=50)  # 'rotten_tomatoes' or 'mubi'
    video_id = models.CharField(max_length=50, blank=True, null=True)  # YouTube ID

    # TMDB Enrichment Fields
    overview = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

## Field Types Explained

### CharField
```python
title = models.CharField(max_length=255)
```
- **What:** Text field with character limit
- **Database type:** VARCHAR(255)
- **Example:** "Dune"
- **Max length:** Required

### TextField
```python
overview = models.TextField(blank=True, null=True)
```
- **What:** Large text field (no limit)
- **Database type:** TEXT
- **Example:** "Epic sci-fi about a desert planet..."
- **Used for:** Summaries, descriptions

### IntegerField
```python
tmdb_id = models.IntegerField(blank=True, null=True, unique=True)
```
- **What:** Whole number
- **Database type:** INTEGER
- **Example:** 438631
- **Constraints:** `unique=True` (no duplicates)

### DateField
```python
release_date = models.DateField(blank=True, null=True)
```
- **What:** Date only (no time)
- **Database type:** DATE
- **Example:** 2021-10-22
- **Format:** YYYY-MM-DD

### DateTimeField
```python
created_at = models.DateTimeField(auto_now_add=True)
```
- **What:** Date and time
- **Database type:** TIMESTAMP
- **Example:** 2025-11-21 14:30:45
- **auto_now_add:** Set once when created
- **auto_now:** Update every time saved

## Field Options

### required vs optional

```python
# REQUIRED (must provide value)
title = models.CharField(max_length=255)

# OPTIONAL (can be blank/null)
overview = models.TextField(blank=True, null=True)
                            ↑             ↑
                    Can leave in form  Can be NULL in database
```

### unique constraint

```python
# No duplicates allowed
tmdb_id = models.IntegerField(unique=True)

# These would fail:
Movie.objects.create(title='Dune', tmdb_id=438631)
Movie.objects.create(title='Dune Part Two', tmdb_id=438631)  # ← ERROR! Already exists
```

### max_length

```python
# String must be 255 characters or less
title = models.CharField(max_length=255)

# Trying to save 256 characters would fail
```

## Database Table

The Movie model creates this table:

```sql
CREATE TABLE movies_movie (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    tmdb_id INTEGER UNIQUE,
    imdb_id VARCHAR(20) UNIQUE,
    source VARCHAR(50) NOT NULL,
    video_id VARCHAR(50),
    overview TEXT,
    release_date DATE,
    poster_path VARCHAR(255),
    backdrop_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Django creates and manages this for you!

## Querying the Database

### Create (INSERT)

```python
# Single create
movie = Movie.objects.create(
    title='Dune',
    video_id='abc123',
    source='rotten_tomatoes',
    release_date='2021-10-22'
)

# Returns: Movie object with id=1, created_at=now, updated_at=now
```

### Read (SELECT)

```python
# Get all movies
all_movies = Movie.objects.all()  # Returns QuerySet of 42 movies

# Get one movie
movie = Movie.objects.get(id=1)  # Returns single Movie object

# Filter movies
rotten_movies = Movie.objects.filter(source='rotten_tomatoes')  # Returns QuerySet

# Get first
first_movie = Movie.objects.first()

# Count
count = Movie.objects.count()  # 42
```

### Update (UPDATE)

```python
# Get and modify
movie = Movie.objects.get(id=1)
movie.title = 'Dune Part Two'
movie.save()  # Updates database

# Or update directly
Movie.objects.filter(id=1).update(title='Dune Part Two')
```

### Delete (DELETE)

```python
# Get and delete
movie = Movie.objects.get(id=1)
movie.delete()

# Or delete directly
Movie.objects.filter(source='mubi').delete()  # Delete all Mubi movies
```

## Meta Class

```python
class Meta:
    ordering = ['-created_at']  # Default ordering (newest first)
```

This controls model behavior:
- **ordering** - Default order when querying
- **verbose_name** - Human-readable name
- **verbose_name_plural** - Plural form
- **db_table** - Custom table name
- **constraints** - Database constraints
- **indexes** - Database indexes

## Instance Methods

```python
def __str__(self):
    return self.title
```

- Called when you print or display the object
- Used in admin interface
- Used in Django shell

```python
movie = Movie.objects.get(id=1)
print(movie)  # Output: "Dune" (calls __str__)
```

## Model Relationships

(Advanced - not used in basic Movie model)

### Foreign Key (One-to-Many)

```python
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField()

# Usage
review = Review.objects.create(movie_id=1, rating=5)
review.movie  # Returns Movie object

# Reverse relationship
movie = Movie.objects.get(id=1)
movie.review_set.all()  # All reviews for this movie
```

### Many-to-Many

```python
class Genre(models.Model):
    name = models.CharField(max_length=50)

class Movie(models.Model):
    genres = models.ManyToManyField(Genre)

# Usage
movie.genres.add(Genre.objects.get(name='Sci-Fi'))
movie.genres.all()  # All genres for this movie
```

## Migrations

When you change a model, Django tracks changes:

```bash
# Create migration (detects changes)
python manage.py makemigrations

# Apply migration (executes SQL)
python manage.py migrate
```

Example migration:

```python
# movies/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ...
            ]
        )
    ]
```

## Model in Context

### How Models Are Used in This Project

```
1. SAVE PHASE
   _fetch_and_save_videos():
   ├─ Get videos from YouTube
   ├─ Check if exists: Movie.objects.filter(title=...)
   └─ Create if new: Movie.objects.create(...)

2. ENRICH PHASE
   enrich_movies_with_tmdb():
   ├─ Find unenriched: Movie.objects.filter(tmdb_id__isnull=True)
   └─ Update: movie.tmdb_id = ...; movie.save()

3. DISPLAY PHASE
   movie_list view:
   ├─ Get all: Movie.objects.all()
   └─ Pass to template: render(request, template, {'movies': movies})
```

## Best Practices

1. **Always provide meaningful field names**
   ```python
   title = models.CharField()  # ✅ Good
   t = models.CharField()      # ❌ Bad
   ```

2. **Use appropriate field types**
   ```python
   release_date = models.DateField()  # ✅ Good
   release_date = models.CharField()  # ❌ Bad (wrong type)
   ```

3. **Make optional fields explicit**
   ```python
   overview = models.TextField(blank=True, null=True)  # ✅ Clear it's optional
   overview = models.TextField()  # ❌ Unclear if required
   ```

4. **Use unique constraints when needed**
   ```python
   tmdb_id = models.IntegerField(unique=True)  # ✅ Prevents duplicates
   ```

5. **Add __str__ method**
   ```python
   def __str__(self):
       return self.title  # ✅ Useful in admin and debugging
   ```

---

Next: [Templates](./07_templates.md)
