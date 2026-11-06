from django import forms

from .models import BookFile
from .validators import validate_pdf

REQUIRED = "دست‌کم یک فایل PDF انتخاب کنید."


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A file field that accepts several files at once (Django docs pattern)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            # An empty selection must still raise the «required» error.
            return [single_clean(item, initial) for item in (data or [None])]
        return [single_clean(data, initial)]


class BookFileUploadForm(forms.Form):
    files = MultipleFileField(
        label="فایل‌های PDF",
        help_text="می‌توانید چند فایل را با هم انتخاب کنید؛ فقط PDF پذیرفته می‌شود.",
        validators=[validate_pdf],
        error_messages={"required": REQUIRED},
        widget=MultipleFileInput(
            attrs={"class": "form-control", "accept": ".pdf,application/pdf"}
        ),
    )

    def save(self, book):
        """Create one BookFile per validated upload and return how many were added."""
        uploads = self.cleaned_data["files"]
        for upload in uploads:
            BookFile.objects.create(
                book=book, file=upload, original_name=upload.name, size=upload.size
            )
        return len(uploads)
