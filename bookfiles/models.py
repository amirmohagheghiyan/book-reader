from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from books.models import Book


def book_file_path(instance, filename):
    """Store each book's files in their own folder: media/books/<book_id>/<filename>."""
    return f"books/{instance.book_id}/{filename}"


class BookFile(models.Model):
    """One PDF file uploaded for a book from this machine."""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="files", verbose_name="کتاب"
    )
    file = models.FileField("فایل", upload_to=book_file_path)
    original_name = models.CharField("نام فایل", max_length=255)
    size = models.PositiveBigIntegerField("حجم (بایت)")
    uploaded_at = models.DateTimeField("زمان بارگذاری", auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at", "pk"]
        verbose_name = "فایل PDF"
        verbose_name_plural = "فایل‌های PDF"

    def __str__(self):
        return self.original_name

    @property
    def size_label(self):
        """Human-readable size in Persian units («۲٫۴ مگابایت»); Django's filter stays English."""
        size = self.size
        for unit in ("بایت", "کیلوبایت", "مگابایت", "گیگابایت"):
            if size < 1024 or unit == "گیگابایت":
                if unit == "بایت":
                    return f"{int(size)} {unit}"
                return f"{size:.1f}".replace(".", "٫") + f" {unit}"
            size /= 1024


@receiver(post_delete, sender=BookFile)
def delete_file_from_disk(sender, instance, **kwargs):
    """Remove the stored file whenever its record goes away, including cascades from Book."""
    instance.file.delete(save=False)
