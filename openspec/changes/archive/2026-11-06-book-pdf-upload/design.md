# Design

## Context

See proposal.md for motivation. Current state that shapes this change:

- `books` owns `Book` (`books/models.py`) and the dashboard at `/`
  (`BookListView` groups an already-ordered queryset with `itertools.groupby`
  and renders one `confirm-modal` per row). Delete is a real POST from the
  shared `templates/components/confirm-modal.html`, whose body text is
  hard-coded to «این کار قابل بازگشت نیست.».
- Shared partials documented in root `design.md`: `page-header`,
  `form-field` (works with any widget that already carries a Bootstrap
  class; file inputs fall into its default branch), `empty-state`,
  `confirm-modal`, `alert`. `base.html` renders Django messages.
- `config/settings.py` has no `MEDIA_ROOT` / `MEDIA_URL`; `.gitignore`
  already ignores `/media/`. `AGENTS.md` prescribes
  `MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "/media/"`, served by
  Django only while `DEBUG = True`.
- Django 6.1.3 is the only dependency. `ClearableFileInput` supports
  `allow_multiple_selected=True`; `django.contrib.humanize` ships with
  Django (no new package).
- `books/jalali.py` exists, but `AGENTS.md` allows Jalali dates only when
  the owner asks; this change does not render calendar dates.

## Goals / Non-Goals

**Goals:**

- A `bookfiles` app that owns the `BookFile` record, its validation, its
  on-disk lifecycle (create and remove), and the per-book files page.
- Validation (PDF-only, all-or-nothing per submission) in the form and a
  validator, not in views or templates.
- Removing a record always removes its file from disk, including when the
  parent `Book` is deleted, without `books` knowing about storage.
- Reuse existing partials and tokens; no new CSS.

**Non-Goals:**

- Reading PDF text, previews, thumbnails, renaming, reordering.
- A file-size cap (proposal open question; none enforced here).
- Serving `media/` outside `DEBUG`; any storage backend other than the
  local filesystem.

## Decisions

### D1. New app `bookfiles` with `BookFile` -> `Book` foreign key

`uv run python manage.py startapp bookfiles`, added to `INSTALLED_APPS`
after `books`. The record lives in its own app per the one-app-per-feature
rule; the FK across apps is ordinary Django. Alternative considered: adding
`BookFile` to `books`. Rejected: `books` would grow storage concerns and
upload views unrelated to the library itself.

### D2. Model `BookFile` (`bookfiles/models.py`)

| Field | Type | Notes |
| --- | --- | --- |
| `book` | `ForeignKey(Book, on_delete=CASCADE, related_name="files")` | «کتاب» |
| `file` | `FileField(upload_to=book_file_path)` | «فایل»; `book_file_path(instance, filename)` returns `books/<book_id>/<filename>` |
| `original_name` | `CharField(max_length=255)` | «نام فایل»: the name as chosen on the owner's computer; shown everywhere instead of the stored path |
| `size` | `PositiveBigIntegerField` | «حجم (بایت)»; copied from the upload at save time |
| `uploaded_at` | `DateTimeField(auto_now_add=True)` | «زمان بارگذاری» |

`Meta`: `ordering = ["uploaded_at", "pk"]` (oldest first, as the spec
orders the list), `verbose_name = "فایل PDF"`, `verbose_name_plural =
"فایل‌های PDF"`. `__str__` returns `original_name`. One initial migration
`bookfiles/migrations/0001_initial.py`; `books` migrations are untouched.

Duplicate names: the default `FileSystemStorage.get_available_name` adds a
random suffix to the stored file, while `original_name` keeps the user's
name, which is exactly the "both kept, same name shown" scenario. Persian
file names survive `get_valid_filename` (it keeps Unicode word characters)
and are never displayed from the stored path anyway.

### D3. Removing files from disk: `post_delete` receiver in `bookfiles/models.py`

```python
@receiver(post_delete, sender=BookFile)
def delete_file_from_disk(sender, instance, **kwargs):
    instance.file.delete(save=False)
```

Django's deletion collector sends `post_delete` for every cascaded row, so
deleting a `Book` (from the dashboard, the edit page, or the admin) removes
each of its files too, and `books` needs no storage code. `FileField.delete`
tolerates a file that is already missing. The now-empty `media/books/<id>/`
folder is left behind (harmless; see Risks). Alternative considered:
overriding `BookFile.delete()`. Rejected: queryset and cascade deletes
bypass it.

### D4. PDF validation (`bookfiles/validators.py`, `bookfiles/forms.py`)

- `validate_pdf(uploaded_file)` raises `ValidationError` with message
  `«%(name)s» فایل PDF نیست. فقط فایل PDF پذیرفته می‌شود.` unless both hold:
  the lower-cased name ends with `.pdf`, and the first five bytes read from
  the upload are `%PDF-` (the file is `seek(0)`-ed afterwards). Standard
  library only; no PDF parser.
- `BookFileUploadForm(forms.Form)` with one field `files`, a
  `MultipleFileField` following the Django documentation pattern
  (`ClearableFileInput(allow_multiple_selected=True)`, `clean` applies the
  single-file clean, including `validate_pdf`, to each upload). Widget
  attrs: `class="form-control"`, `accept=".pdf,application/pdf"`. Label
  «فایل‌های PDF», help «می‌توانید چند فایل را با هم انتخاب کنید؛ فقط PDF
  پذیرفته می‌شود.», `required` error «دست‌کم یک فایل PDF انتخاب کنید.».
  Because every file is validated before anything is saved and the view
  saves inside `transaction.atomic()`, one bad file rejects the whole
  submission (proposal assumption).
- `form.save(book)` creates one `BookFile` per upload with
  `original_name=f.name`, `size=f.size`, and returns the count. Keeping
  creation in the form keeps the view thin.

Alternative considered: `FileExtensionValidator` alone. Rejected: the spec
rejects a renamed non-PDF, which needs the header check.

### D5. Views and URLs (`bookfiles/views.py`, `bookfiles/urls.py`, `app_name = "bookfiles"`)

| URL | Name | View | Template |
| --- | --- | --- | --- |
| `/books/<int:pk>/files/` | `list` | `BookFileListView(FormView)` | `bookfiles/bookfile_list.html` |
| `/books/<int:book_pk>/files/<int:pk>/delete/` | `delete` | `BookFileDeleteView(DeleteView)` | `bookfiles/bookfile_confirm_delete.html` |

- `BookFileListView.setup` loads `self.book = get_object_or_404(Book,
  pk=kwargs["pk"])`. GET renders the page with `book`, `files`
  (`book.files.all()`), the empty form, and breadcrumbs. POST: `form_valid`
  calls `form.save(self.book)` inside `transaction.atomic()`, adds message
  «{count} فایل به «{book.title}» اضافه شد.» and redirects to the same URL;
  `form_invalid` re-renders with the error under the field and the list
  unchanged.
- `BookFileDeleteView.get_queryset` filters
  `BookFile.objects.filter(book_id=self.kwargs["book_pk"])`, so a file pk
  under the wrong book is a 404. `form_valid` adds «فایل «{original_name}»
  حذف شد.»; `get_success_url` returns `bookfiles:list` of that book. GET
  renders the confirm page (same wording as the modal).
- Opening a file is a plain link to `bookfile.file.url` with
  `target="_blank" rel="noopener"`; no view. `config/urls.py` appends
  `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`, which
  Django only honours while `DEBUG` is true, and includes `bookfiles.urls`
  after `books.urls`.
- Unknown book or file: 404 from `get_object_or_404` / the generic view.

Alternative considered: a `CreateView` for upload plus a `ListView`.
Rejected: two views and two templates for one page; the multi-file form is
not a `ModelForm` anyway.

### D6. Dashboard and book deletion (`books/`)

- `BookListView.get_queryset` adds `.annotate(file_count=Count("files"))`;
  grouping is unchanged. Each row gets a third small button «فایل‌ها» with a
  `badge rounded-pill` showing `file_count` (`text-bg-primary` when above
  zero, `text-bg-secondary` when zero), linking to `bookfiles:list`.
- `Book.delete_warning` property (`books/models.py`) returns «این کار قابل
  بازگشت نیست.» when the book has no files and «این کار قابل بازگشت نیست و
  {n} فایل PDF این کتاب هم پاک می‌شود.» otherwise, reading `file_count`
  when annotated and `self.files.count()` otherwise. The wording lives in
  the model, not in three templates.
- `templates/components/confirm-modal.html` gains an optional `text`
  parameter: `{{ text|default:"این کار قابل بازگشت نیست." }}`. The dashboard
  modal, the edit-page modal, and `book_confirm_delete.html` pass
  `book.delete_warning`. The parameter is documented in the root
  `design.md` components table. Existing callers (design-system demo) are
  unaffected.

### D7. Templates (`bookfiles/templates/bookfiles/`)

- `bookfile_list.html`: `page-header` with title «فایل‌های کتاب», lead
  `book.title`, breadcrumbs «کتاب‌های من» then «فایل‌های کتاب». A
  `card-elevated` upload card: `<form method="post"
  enctype="multipart/form-data" novalidate>`, `form-field.html` for
  `form.files`, button «بارگذاری» (`btn-primary`, the page's single primary
  action). Then either `empty-state.html` (title «هنوز فایلی برای این کتاب
  بارگذاری نشده», text «فایل PDF را از بالای همین صفحه انتخاب و بارگذاری
  کنید.», no action) or an `h2` «{{ files|length }} فایل» and a
  `.table-responsive` table (نام فایل، حجم، زمان بارگذاری، کارها) with
  `{{ f.size_label }}` (a model property producing «۲٫۴ مگابایت»; Django's
  `filesizeformat` renders «2.2 MB» in the `fa` locale, checked in the
  browser), `{{ f.uploaded_at|naturaltime }}` inside a `<time datetime>`
  (requires `django.contrib.humanize` in `INSTALLED_APPS`; translated),
  «باز کردن» (`btn-outline-primary btn-sm`, new tab) and «حذف»
  (`btn-outline-danger btn-sm`, opens `confirm-modal` with
  `modal_id="delete-file-<pk>"`, `item_name=f.original_name`,
  `action_url=bookfiles:delete`). One modal per row, as on the dashboard.
- `bookfile_confirm_delete.html`: mirrors `books/book_confirm_delete.html`
  (««{name}» حذف شود؟», «حذف» / «انصراف» back to the files page).
- `books/templates/books/book_list.html`: the «فایل‌ها» button and
  `text=book.delete_warning` on the modal. `book_form.html` and
  `book_confirm_delete.html`: the same warning text.

Relative time («۵ دقیقه پیش») was chosen over a formatted date because
Gregorian dates look wrong in this product and Jalali rendering is not
approved; the exact timestamp stays in the `datetime` attribute.

### D8. Settings (`config/settings.py`)

`MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "/media/"`,
`"django.contrib.humanize"` and `"bookfiles"` in `INSTALLED_APPS`. Django's
default upload handlers already spool files above 2.5 MB to a temporary
file, so large textbooks do not sit in memory. No size-cap settings.

### D9. Admin (`bookfiles/admin.py`)

`@admin.register(BookFile)` with `list_display = ("original_name", "book",
"size", "uploaded_at")`, `list_filter = ("book",)`, `search_fields =
("original_name", "book__title")`. Persian names come from the model.

### D10. Tests (`bookfiles/tests.py`, `books/tests.py`)

All tests run under `override_settings(MEDIA_ROOT=<temporary directory>)`
created in `setUpClass` and removed in `tearDownClass`, so no test touches
the real `media/`. Uploads are `SimpleUploadedFile` objects with
`b"%PDF-1.4\n..."` bodies; no real PDF library and no network.

- Validator: accepts `a.pdf` with a PDF header; rejects `a.docx`, and
  `a.pdf` whose body starts with PNG bytes, with the message naming the file.
- Files page: 404 for an unknown book; empty-state text when no files;
  heading «2 فایل» and oldest-first order; the «باز کردن» link points under
  `/media/`.
- Upload: one file creates one record, the file exists on disk under
  `media/books/<id>/`, message and redirect; three files create three
  records; a `.docx` creates zero records and shows the error text; two
  PDFs plus one bad file create zero records; empty form shows «دست‌کم یک
  فایل PDF انتخاب کنید.».
- Delete: GET shows ««x.pdf» حذف شود؟»; POST removes the record and the
  file from disk, leaves the other file, redirects with message; pk under
  another book is a 404.
- Cascade: deleting the `Book` removes its `BookFile` rows and their files
  from disk.
- Dashboard (`books/tests.py`): row shows `file_count` and the
  `bookfiles:list` link; `delete_warning` text with and without files.
- Admin changelist renders for a superuser created in the test.

## Risks / Trade-offs

- [No size limit: a huge upload fills the disk or takes long] -> local,
  single-user product on the owner's own machine; Django streams uploads to
  temporary files; a cap is a one-line setting if the owner asks (proposal
  open question).
- [Header check can be fooled by a crafted file] -> the goal is a clear
  error for honest mistakes (Word, images), not security; `AGENTS.md`
  forbids calling the product secure.
- [Deleting from disk is irreversible] -> every delete goes through the
  confirm modal naming the file, and the book modal states the file count.
- [`media/books/<id>/` folders stay after their files are deleted] ->
  harmless empty folders under a git-ignored directory; not cleaned up to
  keep the receiver trivial.
- [`naturaltime` / `filesizeformat` wording depends on Django's `fa`
  translations] -> checked in the browser during verification; if a string
  is untranslated, a small model property replaces the filter.
- [`Count("files")` annotation on the dashboard] -> one query with a join;
  fine for a personal library.

## Migration Plan

Fresh feature: `makemigrations bookfiles` then `migrate`. Rollback = remove
the app from `INSTALLED_APPS`, `config/urls.py`, and the dashboard
template, and delete the `media/books/` folder by hand; `books` data is
unaffected.
