from django.contrib import admin

from .models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("summary", "book", "kind", "position", "updated_at")
    list_filter = ("kind",)
    search_fields = ("book__title",)
    ordering = ("book", "position")
