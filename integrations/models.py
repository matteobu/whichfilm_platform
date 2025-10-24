from django.db import models


class YTFilmTitle(models.Model):
    """Store YouTube video titles from a channel"""
    title = models.CharField(max_length=255)
    youtube_video_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title
