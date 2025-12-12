from django.contrib import admin

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "tmdb_id", "imdb_id", "video_id", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("title", "original_title", "tmdb_id", "imdb_id")
    readonly_fields = ("created_at", "updated_at")
