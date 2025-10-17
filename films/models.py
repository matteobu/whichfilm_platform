from django.db import models

class Film(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True)
    original_language = models.CharField(max_length=10, blank=True, null=True)
    origin_country = models.CharField(max_length=10, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    poster_path = models.CharField(max_length=200, blank=True, null=True)
    backdrop_path = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)
    vote_average = models.FloatField(blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title