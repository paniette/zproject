"""
URL configuration for zombicide_editor project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve assets directory
    urlpatterns += static('/assets/', document_root=settings.ASSETS_DIR)
    # Serve bgmapeditor_tiles as static (legacy support)
    urlpatterns += static('/bgmapeditor_tiles/', document_root=settings.BG_MAPEDITOR_TILES_DIR)
