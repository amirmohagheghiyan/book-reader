"""URL configuration for config project (thin: admin + apps)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("books.urls")),  # dashboard at "/"
    path("", include("bookfiles.urls")),  # PDF files of each book
    path("", include("core.urls")),  # shared pages: design system
]

# Uploaded PDFs are served by Django only while DEBUG = True (local use).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
