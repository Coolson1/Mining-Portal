"""Root URL configuration for the project.
This file connects the admin site and the app-level URLs.
"""
from django.contrib import admin
# admin provides the Django admin interface.
from django.urls import path, include
# include lets us reference other URLconfs from apps.
from django.conf import settings
# settings is used to access MEDIA settings for static serving in development.
from django.conf.urls.static import static
# static is a helper to serve media files in development.

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include URLs from the files app at the root path.
    path('', include('files.urls')),
]

if settings.DEBUG:
    # In DEBUG mode, serve media files through Django for convenience.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
