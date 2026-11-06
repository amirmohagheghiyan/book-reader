from django.core.exceptions import ValidationError

PDF_HEADER = b"%PDF-"
NOT_PDF = "«%(name)s» فایل PDF نیست. فقط فایل PDF پذیرفته می‌شود."


def validate_pdf(uploaded_file):
    """Accept only files that are named .pdf and really start with a PDF header."""
    name = uploaded_file.name or ""
    if not name.lower().endswith(".pdf"):
        raise ValidationError(NOT_PDF, code="not_pdf", params={"name": name})
    uploaded_file.seek(0)
    head = uploaded_file.read(len(PDF_HEADER))
    uploaded_file.seek(0)
    if head != PDF_HEADER:
        raise ValidationError(NOT_PDF, code="not_pdf", params={"name": name})
