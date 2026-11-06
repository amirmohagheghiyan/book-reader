# Tasks

## 1. App scaffold and model

- [ ] 1.1 Create the `books` app (`uv run python manage.py startapp books`), add `"books"` to `INSTALLED_APPS` in `config/settings.py`; verify `uv run python manage.py check` passes.
- [ ] 1.2 Write `books/models.py`: `Book` with `title`, `author`, `year` (1300–1500), `month` (`IntegerChoices` with Persian labels), `status` (`TextChoices`, default «در صف»), `pages`, timestamps, `Meta.ordering`, Persian `verbose_name`s, `period_label` and `status_badge_class` properties; verify with model tests in `books/tests.py` (ordering, labels, validators).
- [ ] 1.3 Create and apply the initial migration (`makemigrations books`, `migrate`); verify `makemigrations --check --dry-run` reports no changes.
- [ ] 1.4 Write `books/jalali.py` with `today_jalali()` (pure Python, `timezone.localdate()`); verify unit tests for 2026-03-21 → (1405, 1) and 2026-11-06 → (1404, 8) pass.
- [ ] 1.5 Register `Book` in `books/admin.py` (list_display, list_filter, search_fields); verify `/admin/books/book/` renders with the test client for a superuser created in the test.

## 2. Form, views, URLs

- [ ] 2.1 Write `books/forms.py` `BookForm` with Bootstrap widget classes, `dir="ltr"` on `year`/`pages`, Persian labels and error messages; verify form tests: valid data, blank title, year 1200, pages 0.
- [ ] 2.2 Write `books/views.py`: `BookListView` with `q`/`status` filtering and `(year, month)` grouping in `get_context_data` (`groups`, `has_any_books`, echoed filters); verify list tests for grouping order, search on title and author, status filter, combined filters.
- [ ] 2.3 Add `BookCreateView` (initial from `today_jalali()`), `BookUpdateView`, `BookDeleteView` with Persian success messages and redirect to `books:list`; verify view tests for create (GET defaults, valid POST, invalid POST), update in place, delete POST, delete GET confirm page, unknown pk → 404.
- [ ] 2.4 Write `books/urls.py` (`app_name = "books"`: `list`, `create`, `update`, `delete`) and include it in `config/urls.py` before `core.urls`; verify `reverse("books:list") == "/"` in a test.

## 3. Templates and shared layout

- [ ] 3.1 Write `books/templates/books/book_list.html` using `components/page-header.html`, the GET search/filter form, grouped `.table-responsive` tables with status badges, per-row `components/confirm-modal.html`, and the two states via `components/empty-state.html` (empty library vs no results); verify list tests assert «هنوز کتابی ثبت نشده» vs «کتابی با این مشخصات پیدا نشد» and that the search form is absent when the library is empty.
- [ ] 3.2 Write `books/templates/books/book_form.html` (breadcrumbs, `components/form-field.html` for every field, «ذخیره»/«انصراف», «حذف» + modal on edit) and `books/templates/books/book_confirm_delete.html`; verify create/update tests assert `(الزامی)` markers, prefilled values, and `invalid-feedback` on errors.
- [ ] 3.3 Update `templates/base.html`: brand and «خانه» link to `books:list`, active-item logic by `request.resolver_match.namespace`; remove `HomeView` from `core/views.py`, the `home` route from `core/urls.py`, and `core/templates/core/home.html`; verify `grep -rn "core:home" templates core books` finds nothing and `core/tests.py` (home tests replaced by a `/` → `books:list` test) passes.
- [ ] 3.4 Render `/`, `/books/new/`, `/books/<pk>/edit/` in the browser at phone and desktop width in RTL: grouped headings, badges, modal opens and closes with Escape, form labels attached to fields, no horizontal page scroll, no CDN request; verify by screenshots at both widths and the Django test client assertion `assertNotContains(response, "cdn.")`.

## 4. Verification and documentation

- [ ] 4.1 Run `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`, and `uv run python manage.py test`; verify all pass with the new `books` tests included.
- [ ] 4.2 Walk every scenario in `specs/book-library/spec.md` in the browser at phone and desktop width (create with defaults, blank title, bad year/pages, grouping, search, filter, no results, clear, edit status, cancel delete, confirm delete, deleted pk → 404); verify each outcome matches and note any gap before marking done.
- [ ] 4.3 Update `AGENTS.md` Project Structure (`books/` app, `core/` no longer serves `/`) and root `design.md` only if a token or component rule changed; verify the files describe what is actually in the repo.
- [ ] 4.4 Commit with `feat: monthly book library dashboard`; verify `git status` is clean and `db.sqlite3` is not staged.

## Workflow follow-up

- Run `openspec validate --strict monthly-library`, then `/opsx:verify`.
- Archive the change after verification; archive syncs `specs/book-library`
  into `openspec/specs/`, marks «کتابخانه‌ی ماهانه» as `built` in
  `product.md`, and closes the two related open questions there.
