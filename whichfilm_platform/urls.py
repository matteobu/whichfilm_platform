from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('whichfilm.urls')),  # landing page
    path('films/', include('films.urls')), # films page
]