"""URL configuration for config project (thin: admin + apps)."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("books.urls")),  # dashboard at "/"
    path("", include("core.urls")),  # shared pages: design system
]
