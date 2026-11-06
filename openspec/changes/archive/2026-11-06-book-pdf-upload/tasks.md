# Tasks

## 1. Settings, app scaffold, model

- [x] 1.1 Add `MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "/media/"`, and `"django.contrib.humanize"` to `config/settings.py`; create the app with `uv run python manage.py startapp bookfiles` and add `"bookfiles"` to `INSTALLED_APPS` after `"books"`; verify `uv run python manage.py check` passes.
- [x] 1.2 Write `bookfiles/models.py`: `book_file_path()` (`books/<book_id>/<filename>`), `BookFile` with `book` (FK to `books.Book`, `related_name="files"`, CASCADE), `file`, `original_name`, `size`, `uploaded_at`, `Meta.ordering = ["uploaded_at", "pk"]`, Persian `verbose_name`s, `__str__`, and the `post_delete` receiver that calls `instance.file.delete(save=False)`; verify model tests in `bookfiles/tests.py` (ordering, `__str__`, file removed from a temporary `MEDIA_ROOT` on delete and on cascading `Book` delete) pass.
- [x] 1.3 Create and apply the initial migration (`uv run python manage.py makemigrations bookfiles`, `uv run python manage.py migrate`); verify `uv run python manage.py makemigrations --check --dry-run` reports no changes and no `books` migration was generated.
- [x] 1.4 Register `BookFile` in `bookfiles/admin.py` (`list_display`, `list_filter`, `search_fields` per design D9); verify `/admin/bookfiles/bookfile/` renders with the test client for a superuser created in the test.

## 2. Validation and upload form

- [x] 2.1 Write `bookfiles/validators.py` with `validate_pdf()` (extension `.pdf` and `%PDF-` header, `seek(0)` afterwards, Persian message naming the file); verify validator tests pass for a valid PDF, a `.docx`, and a `.pdf` whose body starts with PNG bytes.
- [x] 2.2 Write `bookfiles/forms.py`: `MultipleFileField` (Django docs pattern with `ClearableFileInput(allow_multiple_selected=True)`), `BookFileUploadForm` with Bootstrap widget attrs, `accept`, Persian label, help, and `required` message, and `save(book)` returning the count; verify form tests pass for one file, three files, no file («دست‌کم یک فایل PDF انتخاب کنید.»), and two good files plus one bad file (invalid, nothing saved).

## 3. Views, URLs, templates

- [x] 3.1 Write `bookfiles/views.py` (`BookFileListView(FormView)` with `setup()` loading the book, `form_valid` saving inside `transaction.atomic()` with message «{n} فایل به «{title}» اضافه شد.», `form_invalid` re-rendering; `BookFileDeleteView(DeleteView)` filtered by `book_pk` with message «فایل «{name}» حذف شد.») and `bookfiles/urls.py` (`app_name = "bookfiles"`: `list`, `delete`); include it in `config/urls.py` after `books.urls` and append `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`; verify view tests pass: unknown book 404, upload redirect and record count, invalid upload keeps count, delete GET confirm text, delete POST removes record and disk file, wrong `book_pk` 404, and `file.url` starts with `/media/`.
- [x] 3.2 Write `bookfiles/templates/bookfiles/bookfile_list.html` (`page-header` with breadcrumbs, upload card with `enctype="multipart/form-data"` and `components/form-field.html`, `components/empty-state.html` when no files, otherwise the «{n} فایل» heading and `.table-responsive` table with `filesizeformat`, `naturaltime` in `<time datetime>`, «باز کردن» in a new tab, «حذف» opening one `components/confirm-modal.html` per row) and `bookfiles/templates/bookfiles/bookfile_confirm_delete.html`; verify template tests assert the empty-state text, the heading «2 فایل», oldest-first order, `id="delete-file-<pk>"`, and the `/media/` link.
- [x] 3.3 Add the optional `text` parameter to `templates/components/confirm-modal.html` (`{{ text|default:"این کار قابل بازگشت نیست." }}`) and update the components table in root `design.md`; verify `core/tests.py` for `/design-system/` still passes and the demo modal still shows the default text.

## 4. Dashboard and book deletion

- [x] 4.1 Add `Book.delete_warning` to `books/models.py` (uses `file_count` when annotated, else `self.files.count()`); add `.annotate(file_count=Count("files"))` to `BookListView.get_queryset` in `books/views.py`; verify tests in `books/tests.py` pass for the warning text with zero and three files and for `file_count` in the dashboard context.
- [x] 4.2 Update `books/templates/books/book_list.html` (the «فایل‌ها» button with the count badge linking to `bookfiles:list`, `text=book.delete_warning` on each modal), `books/templates/books/book_form.html` (modal `text`), and `books/templates/books/book_confirm_delete.html` (warning text); verify dashboard tests assert the `bookfiles:list` link, the badge count, and the «۳ فایل PDF این کتاب هم پاک می‌شود» wording when files exist.

## 5. Integration verification and documentation

- [x] 5.1 Run `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`, and `uv run python manage.py test`; verify all pass with `bookfiles` and the updated `books` tests included, and that no test wrote into the real `media/` folder.
- [x] 5.2 Walk every scenario in `specs/book-files/spec.md` and the two modified requirements in `specs/book-library/spec.md` in the browser (the user's `runserver`) at phone and desktop width in RTL: open the files page from the dashboard, empty state, upload one real PDF, upload three at once, upload a `.docx`, upload a renamed non-PDF, empty form, duplicate name, «باز کردن» in a new tab, cancel and confirm file delete, delete the last file, book modal wording with files, book delete removing files from `media/books/<id>/`, unknown book and file 404; verify each outcome matches, check `naturaltime` and `filesizeformat` render in Persian, no horizontal page scroll, visible focus, and no network request other than localhost.
- [x] 5.3 Update `AGENTS.md` Project Structure (`bookfiles/` app, `media/` now created by this change, settings lines now real) so it matches the repository; verify by reading the section against `ls` output.
- [x] 5.4 Commit with `feat: upload and manage PDF files per book`; verify `git status` is clean and neither `db.sqlite3` nor anything under `media/` is staged.

## Workflow follow-up

- Run `openspec validate --strict book-pdf-upload`, then `/opsx:verify`.
- Archive the change after verification; archive syncs
  `specs/book-files` and the `book-library` delta into `openspec/specs/`
  and marks «آپلود PDF کتاب» as `built` in `product.md`.
