from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Month(models.IntegerChoices):
    FARVARDIN = 1, "فروردین"
    ORDIBEHESHT = 2, "اردیبهشت"
    KHORDAD = 3, "خرداد"
    TIR = 4, "تیر"
    MORDAD = 5, "مرداد"
    SHAHRIVAR = 6, "شهریور"
    MEHR = 7, "مهر"
    ABAN = 8, "آبان"
    AZAR = 9, "آذر"
    DEY = 10, "دی"
    BAHMAN = 11, "بهمن"
    ESFAND = 12, "اسفند"


class Status(models.TextChoices):
    QUEUED = "queued", "در صف"
    READING = "reading", "در حال خواندن"
    DONE = "done", "تمام‌شده"


STATUS_BADGE_CLASSES = {
    Status.QUEUED: "warning",
    Status.READING: "primary",
    Status.DONE: "success",
}

MIN_YEAR = 1300
MAX_YEAR = 1500


class Book(models.Model):
    """A specialized book the owner plans to read in a given Jalali month."""

    title = models.CharField("نام کتاب", max_length=200)
    author = models.CharField("نویسنده", max_length=200, blank=True)
    year = models.PositiveSmallIntegerField(
        "سال",
        validators=[MinValueValidator(MIN_YEAR), MaxValueValidator(MAX_YEAR)],
    )
    month = models.PositiveSmallIntegerField("ماه", choices=Month.choices)
    status = models.CharField(
        "وضعیت", max_length=10, choices=Status.choices, default=Status.QUEUED
    )
    pages = models.PositiveIntegerField(
        "تعداد صفحه", null=True, blank=True, validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین تغییر", auto_now=True)

    class Meta:
        ordering = ["-year", "-month", "title"]
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"

    def __str__(self):
        return self.title

    @property
    def period_label(self):
        """Human label of the reading period, e.g. «آبان ۱۴۰۴»."""
        return f"{self.get_month_display()} {self.year}"

    @property
    def status_badge_class(self):
        """Bootstrap contextual class for the status badge."""
        return STATUS_BADGE_CLASSES.get(self.status, "secondary")

    @property
    def delete_warning(self):
        """Body of the delete confirmation; names the PDF files that go with the book."""
        count = getattr(self, "file_count", None)
        if count is None:
            count = self.files.count()
        if not count:
            return "این کار قابل بازگشت نیست."
        return f"این کار قابل بازگشت نیست و {count} فایل PDF این کتاب هم پاک می‌شود."
