# Tasks

## 1. App scaffold and model

- [ ] 1.1 Create the app with `uv run python manage.py startapp jozveh` and add `"jozveh"` to `INSTALLED_APPS` in `config/settings.py` after `"bookfiles"`; verify `uv run python manage.py check` passes.
- [ ] 1.2 Write `jozveh/models.py`: `Block` with `Kind` choices, `book` (FK, `related_name="blocks"`, CASCADE), `kind`, `position`, `data` (`JSONField`), timestamps, `Meta.ordering = ["position", "pk"]`, Persian `verbose_name`s, `summary`, `template_name`, `__str__`, and `clean()` checking the per-kind `data` shape from design D2; verify model tests in `jozveh/tests/test_models.py` pass for a valid and an invalid shape of every kind and for `summary` truncation.
- [ ] 1.3 Add the ordering methods from design D4 (`Block.append`, `Block.insert_after`, `block.move(direction)`, each in `transaction.atomic()`); verify tests pass for append to empty and non-empty, insert after first, middle, and last, move up and down in the middle, move at both ends returning `False` with no change, ordering after a delete with gaps, and cascade delete with `Book`.
- [ ] 1.4 Create and apply the initial migration (`uv run python manage.py makemigrations jozveh`, `uv run python manage.py migrate`); verify `uv run python manage.py makemigrations --check --dry-run` reports no changes and no `books` or `bookfiles` migration was generated.
- [ ] 1.5 Register `Block` in `jozveh/admin.py` per design D9; verify `/admin/jozveh/block/` renders with the test client for a superuser created in the test.

## 2. Forms for the six kinds

- [ ] 2.1 Write `jozveh/forms.py` with the base class (`to_data()`, `initial_from(data)`), the heading, text, and note forms, and `FORMS_BY_KIND`; verify form tests pass for valid input, empty or whitespace-only input (required error), a heading over 200 characters, and the data ⇄ text round-trip.
- [ ] 2.2 Add `StepsForm`; verify tests pass for three steps, blank lines dropped with numbering intact, an empty field («دست‌کم یک گام بنویسید.»), and the round-trip.
- [ ] 2.3 Add `TableForm`; verify tests pass for a valid table, cell trimming, a short row padded with `""`, a long row erroring with «ردیف 3 بیشتر از سرستون‌ها خانه دارد.», header only («دست‌کم یک ردیف زیر سرستون‌ها بنویسید.»), and the round-trip.
- [ ] 2.4 Add `ConceptMapForm`; verify tests pass for two branches with children split on `،` and `,`, a branch without `:`, a child containing `:` after the first split, an empty center, no branches, and the round-trip.

## 3. Editor, add, edit, move, and delete views

- [ ] 3.1 Write `jozveh/urls.py` (`app_name = "jozveh"`, routes per design D5), the `BookBlocksMixin`, and `JozvehEditorView`; include it in `config/urls.py` after `bookfiles.urls`; verify view tests pass for an unknown book 404, the empty state text «این جزوه هنوز بلوکی ندارد», and blocks rendered in position order.
- [ ] 3.2 Write `BlockKindPickView` and `BlockCreateView` (unknown kind 404, `?after` insert, a missing or other-book `after` falling back to append, message «بلوک «X» اضافه شد.», redirect with `#block-<pk>`); verify tests pass for append, insert after a middle block, a stale `after`, an invalid form re-rendering with no new record, and the `after` value kept from the pick page to the form.
- [ ] 3.3 Write `BlockUpdateView` (initial from `initial_from`, kind and position unchanged, message «بلوک «X» ذخیره شد.»); verify tests pass for a table edit adding a row, an invalid edit leaving data unchanged, and a block of another book returning 404.
- [ ] 3.4 Write `BlockMoveView` (POST only, `direction` up or down else 400, redirect to `#block-<pk>`, no message) and `BlockDeleteView` (GET confirm page, POST delete, message «بلوک حذف شد.»); verify tests pass for up, down, both ends unchanged, GET on move returning 405, a bad direction returning 400, delete of a middle block keeping the order, and delete of the last block showing the empty state.

## 4. Templates and visuals

- [ ] 4.1 Write the six `jozveh/templates/jozveh/blocks/<kind>.html` partials and the `.jozveh-*` styles in `static/css/theme.css` (design D7, tokens only); verify template tests assert `<h2>` for heading, two `<p>` for a two-paragraph text, `.jozveh-note`, an `<ol>` with three `<li>` for steps, `<th>` and `<td>` counts for a table, and center, branch, and child text for a concept map, and that HTML in content is escaped.
- [ ] 4.2 Write `editor.html`, `_block_toolbar.html` (disabled up and down at the ends, `aria-label`s, one `confirm-modal.html` per block with `item_name=block.summary`), `pick.html` (six cards with descriptions), `block_form.html` (`components/form-field.html`, format help, «انصراف» back to the editor), and `block_confirm_delete.html`; verify template tests assert the toolbar links and forms, the `disabled` attribute on the first «بالا» and the last «پایین», `id="delete-block-<pk>"`, and six kind links carrying `?after=` when given.
- [ ] 4.3 Write the standalone `print.html` and the print rules in `theme.css` (`@page`, `.d-print-none` bar, `break-inside: avoid`, `print-color-adjust: exact`), and add the `[data-print]` helper to `static/js/app.js`; verify tests assert that the print page has no navbar or footer, includes the title, the author, every block in order, and the `data-print` button, and shows the empty message for an empty جزوه.

## 5. Dashboard and book deletion

- [ ] 5.1 Change `BookListView.get_queryset` in `books/views.py` to annotate `file_count` and `block_count` with `distinct=True`, and extend `Book.delete_warning` in `books/models.py` to the four sentences of design D8; verify tests in `books/tests.py` pass for a book with 2 files and 5 blocks showing counts 2 and 5 (not 10), and for all four warning sentences, with existing file-count tests still passing.
- [ ] 5.2 Add the «جزوه» button with its count badge to `books/templates/books/book_list.html`, linking to `jozveh:editor`; verify the dashboard test asserts the link and the badge, and that deleting a book via POST removes its blocks.

## 6. Integration verification and documentation

- [ ] 6.1 Run `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`, and `uv run python manage.py test`; verify all pass, including the existing `books`, `bookfiles`, and `core` tests.
- [ ] 6.2 Walk every scenario in `specs/jozveh-editor/spec.md` and the two modified requirements in `specs/book-library/spec.md` in the browser (the user's `runserver`) at phone and desktop width in RTL. Cover: the dashboard «جزوه» button and count, the empty جزوه, all six kinds added with valid and invalid input, adding after a middle block, edit round-trip for table and concept map, up and down including disabled ends and the highlight on the moved block, cancel and confirm delete, the print view and the browser print preview (Persian font, colors, no buttons, no split tables or maps), and book delete wording with files and blocks. Verify each outcome matches, there is no horizontal page scroll, focus is visible, and there is no network request other than localhost.
- [ ] 6.3 Update `AGENTS.md` Project Structure (`jozveh/` app line) and add a «جزوه blocks and print view» subsection to root `design.md` (note, steps, concept map, table, print rules); verify both match the repository by reading them against `ls jozveh` and `theme.css`.
- [ ] 6.4 Commit with `feat: jozveh editor with ordered blocks and print view`; verify `git status` is clean and neither `db.sqlite3` nor `media/` is staged.

## Workflow follow-up

- Run `openspec validate --strict jozveh-editor`, then `/opsx:verify`.
- Archive the change after verification. Archive syncs `specs/jozveh-editor`
  and the `book-library` delta into `openspec/specs/` and marks «ویرایش
  جزوه» as `built` in `product.md`.
