# Design

## Context

See proposal.md for motivation. Current state that shapes this change:

- `core` owns `/` (`HomeView`, `core/templates/core/home.html`, named
  `core:home`) and `/design-system/`. `templates/base.html` links «خانه»
  and the brand logo to `core:home` and marks the active nav item by
  `request.resolver_match.url_name`.
- Shared partials exist and are documented in root `design.md`:
  `page-header`, `form-field` (needs `{% load form_extras %}` and widgets
  that already carry Bootstrap classes), `empty-state`, `confirm-modal`
  (POST form with CSRF, or `demo=True`), `alert` (used by `base.html` for
  Django messages), `card`, `pagination`.
- No main specs exist yet; this change creates the first one
  (`book-library`).
- Only Django is installed. No Jalali library may be added in this change.

## Goals / Non-Goals

**Goals:**

- A `books` app that owns the `Book` record and the dashboard at `/`.
- Thin generic class-based views; validation and display rules in the model
  and `ModelForm`; grouping done in the view, not the template.
- Reuse the existing partials and tokens; no new CSS beyond what
  `theme.css` already provides.

**Non-Goals:**

- Jalali calendar arithmetic beyond "today's Jalali year and month" for form
  defaults. No day-level dates.
- Pagination, sorting controls, bulk actions, import/export.
- Anything about PDF files, جزوه, or AI (later changes and specs).

## Decisions

### D1. New app `books`, `core` keeps only shared pages

`uv run python manage.py startapp books`, added to `INSTALLED_APPS`.
`config/urls.py` becomes:

```python
path("admin/", admin.site.urls),
path("", include("books.urls")),   # dashboard at "/"
path("", include("core.urls")),    # design-system only
```

`core/urls.py` drops the `home` route; `HomeView`, `core/templates/core/home.html`
and its tests are removed. `base.html` points «خانه» and the brand link to
`books:list` and marks the active item with
`request.resolver_match.namespace == "books"`. Alternative considered:
keeping `HomeView` as a redirect to the dashboard. Rejected: dead code and a
second URL for the same page.

### D2. Model `Book` (`books/models.py`)

| Field | Type | Notes |
| --- | --- | --- |
| `title` | `CharField(max_length=200)` | verbose_name «نام کتاب», required |
| `author` | `CharField(max_length=200, blank=True)` | «نویسنده», optional (proposal assumption) |
| `year` | `PositiveSmallIntegerField` | «سال», validators `MinValueValidator(1300)`, `MaxValueValidator(1500)` |
| `month` | `PositiveSmallIntegerField(choices=Month.choices)` | «ماه», `IntegerChoices` 1–12 with Persian labels فروردین … اسفند |
| `status` | `CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)` | «وضعیت»: `queued` «در صف», `reading` «در حال خواندن», `done` «تمام‌شده» |
| `pages` | `PositiveIntegerField(null=True, blank=True)` | «تعداد صفحه», `MinValueValidator(1)` |
| `created_at` / `updated_at` | `DateTimeField(auto_now_add / auto_now)` | housekeeping, not shown |

`Meta`: `ordering = ["-year", "-month", "title"]`, `verbose_name = "کتاب"`,
`verbose_name_plural = "کتاب‌ها"`. Helpers on the model: `__str__` → title,
`period_label` property → «آبان ۱۴۰۴», `status_badge_class` property →
`success` / `primary` / `warning` (keeps the mapping out of templates).
One initial migration `books/migrations/0001_initial.py`.

Alternative considered: a single `period` date field (first day of the
Gregorian month). Rejected: it would need Jalali conversion on every read
and write; two small integers are exactly what the user enters and sorts by.

### D3. Current Jalali year/month without a package (`books/jalali.py`)

A ~25-line pure-Python function `today_jalali() -> tuple[int, int]` using the
standard Gregorian→Jalali day-count algorithm, evaluated with
`django.utils.timezone.localdate()` (`Asia/Tehran`). Used only as the
`initial` value of `year` and `month` on the create form, and covered by a
unit test with two known dates (e.g. 2026-03-21 → 1405/1, 2026-11-06 →
1404/8). Alternative: leave the fields empty. Rejected: the owner enters
the current month almost every time; a wrong default is still editable.
Approved-package alternative (`jdatetime`) is out of scope per
`AGENTS.md`.

### D4. Form (`books/forms.py`)

`BookForm(ModelForm)` with fields `title, author, year, month, status,
pages`. Widgets carry Bootstrap classes so `components/form-field.html`
works unchanged: `form-control` for text/number (`dir="ltr"` and
`inputmode="numeric"` on `year` and `pages`), `form-select` for `month`
and `status`. Labels and error messages in Persian; `year` and `pages`
errors come from the model validators via `ModelForm` (custom
`error_messages` for `required` and `invalid`). The create view passes
`initial` from `today_jalali()`.

### D5. Views and URLs (`books/views.py`, `books/urls.py`, `app_name = "books"`)

| URL | Name | View | Template |
| --- | --- | --- | --- |
| `/` | `list` | `BookListView(ListView)` | `books/book_list.html` |
| `/books/new/` | `create` | `BookCreateView(SuccessMessageMixin, CreateView)` | `books/book_form.html` |
| `/books/<pk>/edit/` | `update` | `BookUpdateView(SuccessMessageMixin, UpdateView)` | `books/book_form.html` |
| `/books/<pk>/delete/` | `delete` | `BookDeleteView(DeleteView)` | `books/book_confirm_delete.html` |

- `BookListView.get_queryset` applies `q` (`Q(title__icontains) |
  Q(author__icontains)`) and `status` (only when it is a valid choice) from
  `request.GET`. `get_context_data` adds `groups`: a list of
  `{"label": «آبان ۱۴۰۴», "books": [...]}` built with `itertools.groupby`
  over the already-ordered queryset keyed by `(year, month)`; plus `q`,
  `status`, `status_choices`, `has_any_books` (unfiltered `exists()`) so
  the template can tell "empty library" from "no results".
- Create/update redirect to `books:list` with messages «کتاب «X» ذخیره
  شد.»; delete posts from the shared `confirm-modal` on the list page and
  on the edit page, and the GET fallback renders `book_confirm_delete.html`
  (same component, no modal). Success message «کتاب «X» حذف شد.» is added
  in `form_valid` (Django 6 `DeleteView` uses `FormMixin`).
- Unknown `pk` → 404 from the generic views; Django's default 404 page is
  acceptable for this local product (no custom template in this change).

Alternative considered: grouping in the template with `{% regroup %}`.
Rejected: label formatting (Persian month name + year) belongs in Python
and is easier to test.

### D6. Templates (`books/templates/books/`)

- `book_list.html`: `page-header` (title «کتاب‌های من», lead, action
  «افزودن کتاب»). If `has_any_books` is false → `empty-state` only.
  Otherwise a GET form (`role="search"`) with the text input, a status
  `form-select`, buttons «جستجو» and, when filters are active, «پاک کردن
  جستجو» linking to `books:list`. Then, per group, an `h2` with the period
  label and a `.table-responsive` table (نام، نویسنده، صفحه، وضعیت، کارها)
  using `.badge.text-bg-<status_badge_class>`; on phones the same table
  scrolls horizontally (as on `/design-system/`). No-results state uses
  `empty-state` with the «پاک کردن جستجو» action. One `confirm-modal` per
  book row (`modal_id="delete-book-<pk>"`, `action_url=books:delete`).
- `book_form.html`: `page-header` with breadcrumbs (خانه ‹ افزودن/ویرایش),
  the form through `form-field.html`, buttons «ذخیره» (primary) and
  «انصراف» (outline, back to list); on the edit page a «حذف» danger button
  opening the `confirm-modal`.
- `book_confirm_delete.html`: heading ««X» حذف شود؟», warning text, POST
  form with «حذف» and «انصراف».
- `base.html`: nav/brand links to `books:list`; active logic by namespace;
  «سیستم طراحی» link unchanged.

### D7. Admin (`books/admin.py`)

`@admin.register(Book)` with `list_display = ("title", "author", "year",
"month", "status", "pages")`, `list_filter = ("status", "year", "month")`,
`search_fields = ("title", "author")`. Persian names come from the model.

### D8. Tests (`books/tests.py`, `core/tests.py`)

- Model: ordering, `period_label`, `status_badge_class`, validators.
- `today_jalali()`: two fixed dates.
- List: `/` returns 200 with the list template; grouping order and labels;
  `q` on title and on author; `status` filter; combined; empty state text
  vs no-results text; filter values echoed in the form.
- Create: GET has defaults; valid POST redirects and creates; blank title
  and year 1200 / pages 0 re-render with errors and create nothing.
- Update: GET prefilled; POST changes status in place (count unchanged).
- Delete: POST removes and redirects with message; GET shows confirm page;
  unknown pk → 404.
- `core/tests.py`: drop home tests, keep design-system tests, add a test
  that `/` is served by `books:list`.
  Every test uses the Django test client only; no network, no browser.

## Risks / Trade-offs

- [Grouping in Python loads all books] → fine for one person's library
  (tens to low hundreds of rows); pagination is a later change if needed.
- [Pure-Python Jalali helper could be wrong around Nowruz] → unit tests on
  known dates; it only sets a form default the user can change.
- [One modal per row inflates the list HTML] → acceptable at this scale;
  keeps delete a real POST with CSRF and no custom JavaScript.
- [Removing `core:home` breaks any template still linking to it] → grep for
  `core:home` and `url_name == 'home'` is part of the tasks; tests render
  both remaining pages.
- [Author optional may hide data-entry mistakes] → shown as «—» in the
  table; the owner can tighten it later in a small change.

## Migration Plan

Fresh feature: `makemigrations books` then `migrate`. Rollback = remove the
app from `INSTALLED_APPS` and `config/urls.py` and restore `HomeView`
from git; no data to migrate.
