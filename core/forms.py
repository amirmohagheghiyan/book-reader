from django import forms

STATUS_CHOICES = [
    ("", "انتخاب کنید"),
    ("queued", "در صف"),
    ("reading", "در حال خواندن"),
    ("done", "تمام‌شده"),
]


class DesignSystemSampleForm(forms.Form):
    """Sample form that only demonstrates the shared form-field component."""

    title = forms.CharField(
        label="عنوان",
        max_length=120,
        help_text="نامی که در فهرست نمایش داده می‌شود.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="ایمیل",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "dir": "ltr"}),
    )
    pages = forms.IntegerField(
        label="تعداد صفحه",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "dir": "ltr"}),
    )
    status = forms.ChoiceField(
        label="وضعیت",
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    note = forms.CharField(
        label="یادداشت",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    remind = forms.BooleanField(
        label="یادآوری ماهانه فعال باشد",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
