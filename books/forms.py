from django import forms

from .models import Book, Month

REQUIRED = "این فیلد لازم است."
INVALID_NUMBER = "یک عدد وارد کنید."


class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No «---------» placeholder: the month list is always one of the twelve months.
        self.fields["month"].choices = Month.choices

    class Meta:
        model = Book
        fields = ["title", "author", "year", "month", "status", "pages"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(
                attrs={"class": "form-control", "dir": "ltr", "inputmode": "numeric"}
            ),
            "month": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "pages": forms.NumberInput(
                attrs={"class": "form-control", "dir": "ltr", "inputmode": "numeric"}
            ),
        }
        help_texts = {
            "year": "سال شمسی با چهار رقم.",
            "pages": "اختیاری؛ برای تخمین حجم خواندن.",
        }
        error_messages = {
            "title": {"required": REQUIRED},
            "year": {
                "required": REQUIRED,
                "invalid": INVALID_NUMBER,
                "min_value": "سال باید بین ۱۳۰۰ تا ۱۵۰۰ باشد.",
                "max_value": "سال باید بین ۱۳۰۰ تا ۱۵۰۰ باشد.",
            },
            "month": {"required": REQUIRED, "invalid_choice": "ماه را از فهرست انتخاب کنید."},
            "status": {"required": REQUIRED, "invalid_choice": "وضعیت را از فهرست انتخاب کنید."},
            "pages": {
                "invalid": INVALID_NUMBER,
                "min_value": "تعداد صفحه باید دست‌کم ۱ باشد.",
            },
        }
