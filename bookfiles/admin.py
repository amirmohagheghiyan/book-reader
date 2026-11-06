from django.contrib import admin

from .models import BookFile


@admin.register(BookFile)
class BookFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "book", "size", "uploaded_at")
    list_filter = ("book",)
    search_fields = ("original_name", "book__title")
