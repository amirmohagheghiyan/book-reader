# Design

## Context

See `proposal.md` (Why) and `specs/jozveh-editor/spec.md` for behavior.
Current state relevant to the approach:

- `books.Book` is the root record. `bookfiles.BookFile` hangs off it with
  `related_name="files"` and CASCADE. The dashboard (`BookListView`)
  annotates `file_count=Count("files")` and re-applies `Meta.ordering`.
- `Book.delete_warning` builds the confirm-modal body from `file_count` (or
  `self.files.count()`). `book_list.html`, `book_form.html` and
  `book_confirm_delete.html` render it.
- Shared partials exist: `page-header`, `empty-state`, `form-field`,
  `confirm-modal` (with optional `text`). `base.html` has the navbar, the
  footer and messages. Bootstrap's JS bundle and `static/js/app.js`
  (28 lines) are loaded on every page.
- Constraints:
  - No JS framework, REST API or new package.
  - Files of roughly 200 lines or fewer.
  - Business rules live in models and forms.
  - Colors only from the `design.md` tokens.

## Goals / Non-Goals

**Goals:**

- One storage shape for all six block kinds that the AI change (capability
  4) can write without any schema change.
- Plain server-rendered forms for every kind, including the structured
  ones, with a text format that round-trips exactly between the stored
  data and the edit form.
- One rendering partial per kind, shared by the editor and the print view,
  so both views always look the same.
- Ordering operations (append, insert after, move up and down, delete) that
  stay correct and atomic.

**Non-Goals:**

- No client-side editing, drag-and-drop or live preview.
- No rich text and no Markdown parsing.
- No generic "page builder" abstraction beyond the six kinds.
- No `Jozveh` container model (see D1).

## Decisions

### D1. App `jozveh`, one model `Block`, linked straight to `Book`

The new app is `jozveh/` (`startapp jozveh`), added to `INSTALLED_APPS`
after `bookfiles`. It has one model:

```python
class Block(models.Model):
    class Kind(models.TextChoices):
        HEADING = "heading", "عنوان"
        TEXT = "text", "متن"
        NOTE = "note", "نکته"
        STEPS = "steps", "مراحل"
        TABLE = "table", "جدول"
        CONCEPT_MAP = "concept_map", "نقشه‌ی مفهومی"

    book = FK(Book, CASCADE, related_name="blocks", verbose_name="کتاب")
    kind = CharField("نوع", max_length=20, choices=Kind.choices)
    position = PositiveIntegerField("جایگاه")
    data = JSONField("محتوا", default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "pk"]
        verbose_name = "بلوک جزوه"
        verbose_name_plural = "بلوک‌های جزوه"
```

A book's جزوه is simply `book.blocks.all()`.

- *Alternative:* a `Jozveh` one-to-one model holding the blocks. Rejected
  because nothing would be stored on it today; "every book has one جزوه"
  falls out of the FK. The AI change can add a container later through a
  new migration if it needs per-جزوه metadata.
- *Alternative:* one model per kind, or typed columns. Rejected because the
  AI writes heterogeneous blocks as a list, and six tables would make
  ordering across kinds painful.

### D2. `data` JSON shape per kind (the contract with capability 4)

| kind | `data` |
| --- | --- |
| heading | `{"text": str}` |
| text, note | `{"text": str}` (paragraphs split on blank lines at render time) |
| steps | `{"items": [str, ...]}` (at least 1) |
| table | `{"header": [str, ...], "rows": [[str, ...], ...]}` (every row padded to `len(header)`, at least 1 row) |
| concept_map | `{"center": str, "branches": [{"label": str, "children": [str, ...]}, ...]}` (at least 1 branch) |

- `Block.clean()` checks the shape against this table, so admin edits and
  future AI writes are validated by the same rules as the forms.
- `Block.summary` is a property returning the kind label plus the first
  ~40 characters of the main text (`text`, `items[0]`, `header` joined, or
  `center`). The confirm modal uses it as `item_name`, and admin uses it as
  `__str__`.

### D3. One form per kind, mapping text ⇄ data

`jozveh/forms.py` holds a small base class with `to_data()` and the class
method `initial_from(data)`, plus one plain `forms.Form` per kind. A
`FORMS_BY_KIND` dict maps each kind to its form.

- **heading:** `text` is a `CharField(max_length=200)`.
- **text, note:** `text` is a `CharField(widget=Textarea)`.
- **steps:** `items` is a textarea. Lines are stripped, blanks dropped, and
  an empty result raises «دست‌کم یک گام بنویسید.».
- **table:** `rows` is a textarea.
  - Non-blank lines are split on `|` and cells are stripped.
  - The first line is the header. No data rows raises «دست‌کم یک ردیف زیر
    سرستون‌ها بنویسید.».
  - A row longer than the header raises «خط {n} بیشتر از سرستون‌ها خانه
    دارد.», where n is the line number in the textarea as typed (header and
    blank lines included), so it matches what the user sees. It says «خط»
    (line), not «ردیف» (row), because a user counting table rows would not
    count the header.
  - Shorter rows are padded with `""`.
- **concept_map:** `center` is a `CharField(max_length=200)` and `branches`
  is a textarea.
  - Each non-blank line is split on the first `:`, and children are split
    on `،` or `,`, then stripped with blanks dropped.
  - A line without `:` is a branch with no children.
  - No branch at all raises an error under `branches`.
- **Initial values for edit:** `initial_from()` joins items with newlines,
  rows with ` | `, and children with `، `, so data → text → data is
  identity. Tests assert this round-trip for every kind.

Widgets get the Bootstrap classes in the form, as `bookfiles` already
does. Help text under each structured textarea shows the format with a
short example.

- *Alternative:* a `ModelForm` on `Block` with a raw JSON field. Rejected
  because a non-technical user cannot write JSON.
- *Alternative:* Django formsets for table rows and branches. Rejected
  because they need JS to add rows to be usable and are heavy on phones.

### D4. Ordering lives on the model, inside transactions

These are `Block` methods (and one class method), each in
`transaction.atomic()`:

- `Block.append(book, kind, data)`: `position = max(position) + 1`, or 1 when
  the جزوه is empty.
- `Block.insert_after(anchor, kind, data)`: runs
  `book.blocks.filter(position__gt=anchor.position).update(position=F("position") + 1)`,
  then creates the new block at `anchor.position + 1`.
- `block.move(direction)`: finds the neighbor by ordering (`position__lt`
  ordered desc, or `position__gt` ordered asc). If there is none it does
  nothing and returns `False`; otherwise it swaps the two positions and
  saves both.
- Delete leaves gaps, which is harmless because ordering only compares
  values.

No `UniqueConstraint(book, position)`. SQLite checks uniqueness row by row
during `F()` shifts and swaps, which would need temporary positions.
Ordering by `("position", "pk")` keeps display deterministic even if a
duplicate ever appears (for example from admin edits).

### D5. URLs and views (`jozveh/urls.py`, `app_name = "jozveh"`)

All routes live under `books/<int:pk>/jozveh/`. The book is loaded in
`setup()` with `get_object_or_404`, and blocks are always fetched through
`book.blocks`, so a block of another book is a 404.

| name | path | view | method |
| --- | --- | --- | --- |
| `editor` | `` | `JozvehEditorView(TemplateView)` | GET |
| `pick` | `add/` | `BlockKindPickView(TemplateView)`; keeps `?after=<id>` | GET |
| `add` | `add/<kind>/` | `BlockCreateView(FormView)`; 404 on unknown kind; `?after=<id>` → `insert_after`, missing or other-book id → `append` | GET/POST |
| `edit` | `blocks/<int:block_pk>/edit/` | `BlockUpdateView(FormView)` | GET/POST |
| `move` | `blocks/<int:block_pk>/move/` | `BlockMoveView(View)`; `direction` ∈ {up, down}, else 400 | POST only |
| `delete` | `blocks/<int:block_pk>/delete/` | `BlockDeleteView(DeleteView)`; GET confirm page, POST delete | GET/POST |
| `print` | `print/` | `JozvehPrintView(TemplateView)` | GET |

- Success redirects go to `editor` with `#block-<pk>`.
- Messages:
  - «بلوک «{kind label}» اضافه شد.» after adding.
  - «بلوک «{kind label}» ذخیره شد.» after editing.
  - «بلوک حذف شد.» after deleting.
- Move shows no message (proposal assumption). Its redirect anchor
  `#block-<pk>` plus a `:target` highlight in `theme.css` keep the user on
  the moved block.
- `config/urls.py` includes `jozveh.urls` after `bookfiles.urls`.
- Kept below ~200 lines: `views.py` holds a small `BookBlocksMixin` (book
  in `setup()`, breadcrumbs, `get_block()`) shared by all views.

### D6. Templates

```
jozveh/templates/jozveh/
  editor.html              page-header (title «جزوه‌ی «X»», actions: «افزودن بلوک», «نمای چاپ»), empty-state or block list
  _block_toolbar.html      up/down POST forms (disabled at ends), edit, delete (modal), «افزودن بعد از این»
  pick.html                six cards (components/card.html) linking to add/<kind>/?after=
  block_form.html          one template for add and edit; loops form fields with components/form-field.html
  block_confirm_delete.html
  print.html               standalone document (does NOT extend base.html)
  blocks/heading.html  blocks/text.html  blocks/note.html
  blocks/steps.html    blocks/table.html blocks/concept_map.html
```

- `editor.html` and `print.html` both render each block with
  `{% include block.template_name %}`. `Block.template_name` is a property
  returning `jozveh/blocks/<kind>.html`.
- Each block in the editor is a `<section id="block-<pk>"
  class="jozveh-block">` followed by its toolbar.
- Up and down buttons carry an `aria-label` naming the block summary.
  Toolbar buttons are `btn-sm` and wrap with `flex-wrap gap-2` on phones.
- One `confirm-modal.html` per block (`modal_id="delete-block-<pk>"`),
  the same pattern as the files page.
- `print.html` loads the same local `bootstrap.rtl.min.css`, `theme.css`
  and `app.js`, with `<html lang="fa" dir="rtl">` and
  `<body class="jozveh-print">`. A `.d-print-none` bar holds the «چاپ یا
  ذخیره‌ی PDF» button (`data-print`) and the «بازگشت به ویرایش» link.
  Then come the title, the author and the blocks.
- The heading block renders as `h2` and the page title as `h1`, so heading
  levels are not skipped. Text and note use the `linebreaks` filter, which
  escapes content and turns blank-line-separated text into `<p>`s.

### D7. Visuals and print rules in `theme.css`

All new rules use existing tokens only. Classes:

- `.jozveh-block`: spacing and a `:target` outline or soft highlight
  (`--bs-primary-bg-subtle`) for the moved or added block.
- `.jozveh-note`: background `--bs-primary-bg-subtle`, `border-inline-start`
  4px `--bs-primary`, `--bs-border-radius`.
- `.jozveh-steps`: an `ol` with numbered circles (`--bs-primary` background,
  white text), with a connector line on the inline-start side.
- `.jozveh-map`: the center box on a `--jz-gradient-brand` background with
  white text, which is a highlighted element, not running text. Below it
  sits a CSS grid of branch cards (`repeat(auto-fit, minmax(12rem, 1fr))`),
  each a bordered box with its children as a small list. Short connector
  lines use borders, with no SVG or JS. On phones the branches stack in one
  column.
- Tables use Bootstrap `.table .table-bordered` inside `.table-responsive`.
  In print `.table-responsive` loses `overflow`.
- Print (`@media print`):
  - `@page { margin: 1.5cm; }`.
  - Body background is white.
  - Shadows are removed.
  - `print-color-adjust: exact` keeps the note and map colors.
  - `break-inside: avoid` applies to `.jozveh-note`, `.jozveh-steps`,
    `.jozveh-map` and `table`.
  - `break-after: avoid` applies to headings.

`app.js` gets one helper: any `[data-print]` element calls `window.print()`
on click.

### D8. Dashboard and book deletion

- `BookListView.get_queryset` annotates
  `file_count=Count("files", distinct=True)` and
  `block_count=Count("blocks", distinct=True)`. `distinct` is required
  because two joined reverse FKs multiply rows.
- `book_list.html` gets a «جزوه» button with a count badge before «فایل‌ها».
  It links to `jozveh:editor` and is styled like the files button.
- `Book.delete_warning` reads `file_count` and `block_count` when annotated
  and otherwise counts. It returns one of four sentences:
  - neither: «این کار قابل بازگشت نیست.»
  - files only: the existing sentence, unchanged.
  - blocks only: «… و جزوه‌ی این کتاب ({n} بلوک) هم پاک می‌شود.»
  - both: «… و {f} فایل PDF و جزوه‌ی این کتاب ({n} بلوک) هم پاک می‌شود.»
- `books/models.py` refers to `self.blocks`. `books` must not import
  `jozveh`, so there is no circular import.
- There is no `books` migration (no field change).

### D9. Admin

`jozveh/admin.py` registers `Block` with:

- `list_display = ("summary", "book", "kind", "position", "updated_at")`
- `list_filter = ("kind",)`
- `search_fields = ("book__title",)`
- `ordering = ("book", "position")`

`Block.clean()` (D2) guards raw JSON edits there.

## Risks / Trade-offs

- **The text formats are a mini-syntax the user must learn.** → Each
  structured field shows a one-line format and an example in its help
  text, and errors name the line number. The AI change will fill most
  blocks anyway.
- **Literal `|`, `:` or `،` inside a cell, branch or child cannot be
  typed.** → This is accepted for now. Only the first `:` splits a branch
  line, so children may contain `:`.
- **Large concept maps (many branches or children) get tall on paper.** →
  `break-inside: avoid` may push a big map to the next page, which is
  acceptable. A map taller than a page still breaks, and browsers handle
  that.
- **Browser print differences, such as Persian font embedding in "Save as
  PDF".** → `@font-face` is local and loaded before printing. Manual check
  in Chrome and Edge is part of verification, and other browsers are
  reported as unchecked.
- **Concurrent edits in two tabs could produce duplicate positions.** →
  This is single-user and local. Ordering by `(position, pk)` stays
  deterministic, and the next move repairs the pair.
- **`JSONField` on SQLite needs the JSON1 extension.** → It is bundled
  with the Python 3 sqlite builds used here. `manage.py check` fails loudly
  if it is missing.

## Migration Plan

- `makemigrations jozveh` creates `0001_initial` and `migrate` applies it.
  No existing data changes.
- Rollback: remove the app from `INSTALLED_APPS` and URLs. The `books`
  and `bookfiles` tables are untouched.
