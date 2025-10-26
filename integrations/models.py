from django.db import models


class SourceFilmTitle(models.Model):
    """Store film titles from various sources (YouTube, festivals, etc.)"""
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    original_title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=50)  # 'youtube', 'festival', etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ['-year', 'title']
