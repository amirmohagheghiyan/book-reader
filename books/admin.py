from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "year", "month", "status", "pages")
    list_filter = ("status", "year", "month")
    search_fields = ("title", "author")
