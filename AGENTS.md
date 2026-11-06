# AGENTS.md — Django + Bootstrap Workshop Project

## Purpose

A Persian, right-to-left web product built with Django and Bootstrap in one
codebase: Django renders pages on the server, Bootstrap styles them. It is
built in a workshop by a non-technical product owner who does not write code.
The project runs locally only; its single allowed outbound call is the AI
service described in Current Boundary. Do not invent features or behavior
that the user or an approved spec did not describe.

## Current Boundary

Build only what the current request or approved change asks for. Out of scope
unless the user explicitly asks:

- Deployment, hosting, domains, HTTPS, production settings, Docker, CI.
- Sign-up, login, password reset, roles, per-user data. The only account is a
  local superuser the user creates for the Django admin.
- Email, payments, and any network request made by the running product other
  than the single AI-service call allowed below (no CDN, analytics, fonts, or
  other external APIs).
- File uploads other than the PDF upload allowed below (no images, Word,
  EPUB, or cloud storage).
- A separate frontend app, a REST API, JavaScript frameworks, or a Node.js
  build step. Bootstrap is used as ready-made local static files.
- Python packages other than Django. Each new package needs the user's
  explicit approval and is added in its own OpenSpec change, one package per
  change, with the reason recorded in that change's `design.md`; check
  `pyproject.toml` first.

### Allowed by the owner's decision (2026-11-06)

- **PDF upload on this machine.** The user uploads a book as a PDF file from
  the same computer the product runs on. Files are stored locally under
  `media/` (git-ignored) and never sent anywhere except to the AI service
  below as part of building a جزوه. Only `.pdf` is accepted.
- **One AI service.** The running product may make exactly one kind of
  network request: calling an AI model to build a جزوه from a book. The
  service address, model name, and key are read from a git-ignored `.env`
  (`AI_BASE_URL`, `AI_MODEL`, `AI_API_KEY`); nothing provider-specific is
  hard-coded. Today the target is Google AI Studio; later it will be a local
  Ollama, and that switch must need only `.env` edits. How `.env` is loaded
  and how the request is sent (a package or the standard library) is decided
  in the OpenSpec change that adds the call, under the package rule above.

Never describe this project as production-ready or secure: it has no login, so
anyone who can open the local address can change the data, upload files, and
trigger AI calls that may cost money on the owner's key.

A spec, plan, or task cannot override this boundary. If one needs something
out of scope, stop and report the conflict.

## Read Before Editing

1. This file, completely.
2. `product.md` — approved product context, not approval to build every
   planned capability.
3. `design.md` — for every visual change.
4. `openspec/config.yaml`, the relevant specs in `openspec/specs`, and the
   active change in `openspec/changes` (proposal, specs, design, tasks).
5. The relevant Django app and the shared `templates/` before creating
   anything new.

If the coding tool reads another instruction file (for example `CLAUDE.md`),
that file only points here (`@AGENTS.md`); do not duplicate rules in it.

## Workshop Setup Order

1. Prompt 1 (`prompts/prompt-1-docs-and-django.md`): fill `product.md` from
   the owner's idea, align all documents, and build the Django + Bootstrap
   base with empty `static/fonts/` and `static/brand/`.
2. The owner places font files in `static/fonts/` and the logo in
   `static/brand/`.
3. Prompt 2 (`prompts/prompt-2-design-system.md`): tokens, font, logo,
   shared components, and the `/design-system/` page.
4. Every product capability after that goes through the OpenSpec cycle.

## Talking With the User

The user is a non-technical product owner. Every OpenSpec command and direct
request is a conversation in plain Persian.

- Reply in fluent, friendly, everyday Persian. Keep file names, commands, and
  code in English. Explain an unavoidable technical term in one short phrase.
- Ask only product questions: who uses it, what they see and do, which rules
  and states apply, what is out of scope. Decide technical details yourself
  from this file, `design.md`, and the existing code; mention them briefly.
- Ask at most three questions at a time, with short options and one marked
  «پیشنهادی». If the user answers «نمی‌دانم», propose a safe default and ask
  for confirmation.
- Never ask for passwords, tokens, or secrets. The user types the superuser
  password in their own terminal.
- End each reply with: what was done, what to open or try, and the exact next
  command or prompt.

## Spec-Driven Development (OpenSpec)

- Use the cycle for: a new feature or page with real behavior, a change in how
  something works, new or changed stored data, access rules.
- Use a direct request for: setup and infrastructure, the design system, text,
  color, or spacing tweaks, a bug whose correct behavior is already known.
- Cycle: `/opsx:explore` (optional) → `/opsx:propose` → user review and
  update → `/opsx:apply` (fresh conversation) → user testing →
  `openspec validate --strict <change>` → `/opsx:verify` → `/opsx:archive`.
- Proposal and spec prose are plain Persian. OpenSpec headings, SHALL/MUST,
  GIVEN/WHEN/THEN, code, paths, and commands stay English. A change's
  `design.md` and `tasks.md` are English.
- A change's `design.md` is its technical plan only; the shared visual system
  is the root `design.md`.
- No code during propose or update. Mark a task done only after its work and
  checks pass. Do not archive with an unresolved CRITICAL verify finding.

## Project Structure

```text
manage.py  pyproject.toml  uv.lock  AGENTS.md  design.md  product.md
CLAUDE.md               # one line: @AGENTS.md
config/                 # Django project: settings.py, urls.py, wsgi.py, asgi.py
templates/
  base.html             # shared layout (RTL, Bootstrap, navbar, footer)
  components/           # reusable partials: alert, card, form-field, ...
media/                  # uploaded PDF files (git-ignored; created by the upload change)
.env                    # AI_BASE_URL, AI_MODEL, AI_API_KEY (git-ignored; never committed)
static/
  css/theme.css         # @font-face, tokens and Bootstrap overrides from design.md
  css/vendor/           # bootstrap.rtl.min.css (local copy)
  js/app.js             # tiny helpers: tooltips, toasts, swatch color codes
  js/vendor/            # bootstrap.bundle.min.js (local copy)
  fonts/                # YekanBakhFaNum-*.woff2 (placed by the user)
  brand/                # aleflogo.png (placed by the user)
core/                   # home page, design-system page and shared pages
  forms.py              # sample form used only by the design-system page
  templatetags/form_extras.py   # `add_class` filter for form-field.html
  templates/core/home.html
  templates/core/design-system.html
  templates/core/design-system/  # one partial per UI-kit section
<feature>/              # one Django app per product feature
openspec/               # config.yaml, specs/, changes/
```

- One app per feature: `uv run python manage.py startapp <feature>`, then add
  it to `INSTALLED_APPS`. Keep `config/urls.py` thin (include each app).
- Markup used by two or more pages goes in `templates/components/`.

## Code Rules

- Python files snake_case; templates, CSS, JS, fonts kebab-case where we name
  them. Files roughly 200 lines or fewer.
- Prefer small class-based generic views and `ModelForm`. Business rules live
  in models or forms, not templates.
- Data-changing views use POST with `{% csrf_token %}` and redirect after
  success. Delete always asks for confirmation.
- Show success and failure with `django.contrib.messages`.
- Register each model in `admin.py` with a Persian `verbose_name`.
- Model changes: `makemigrations` then `migrate`. Never edit an applied
  migration; add a new one. `db.sqlite3` is not committed.
- No secrets in code or chat. The AI key and settings live only in the
  git-ignored `.env`; code reads them from the environment and never logs or
  renders them. The user edits `.env` themselves; never ask for its values.
- Every call to the AI service goes through one small module in the app that
  owns the جزوه; views and templates never call the service directly. Tests
  replace that module with a fake and never reach the network.

## Django Settings

- `LANGUAGE_CODE = "fa"`, `TIME_ZONE = "Asia/Tehran"`, `USE_I18N = True`,
  `USE_TZ = True`.
- SQLite. `DEBUG = True` is acceptable (local only).
- `TEMPLATES["DIRS"]` includes `templates/`; `STATICFILES_DIRS` includes
  `static/`.
- Uploaded PDFs: `MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "/media/"`,
  served by Django only while `DEBUG = True` (added by the upload change).
- Jalali dates only if the user asks; a Jalali library needs approval.

## Tooling and Git

- Python and packages only with uv: `uv run python manage.py ...`. No pip.
- The user runs `uv run python manage.py runserver` in their own terminal. Do
  not leave a server running; tell the user what to open or refresh.
- The user creates the superuser (`createsuperuser`) themselves.
- Bootstrap and font files may be downloaded once during setup into
  `static/`; the running product loads nothing from the internet except the
  AI-service call allowed in Current Boundary.
- Commit after each verified step (the message the prompt gives, or a short
  conventional one). No remote; never push.
- If Git has no identity, set a repository-local one only
  (`Workshop Participant` / `participant@workshop.local`).
- Never discard, reset, or rewrite commits without the user's explicit choice.

## Design and RTL

- `<html lang="fa" dir="rtl">`, `bootstrap.rtl.min.css`, logical utilities
  (`ms-*`, `me-*`, `ps-*`, `pe-*`, `text-start`, `text-end`).
- Colors, radius, and font come from `design.md` tokens via CSS variables in
  `static/css/theme.css`. No hard-coded colors, no second visual system.
- Bootstrap components first; custom CSS only in `theme.css`.
- Every page works on phone and desktop, with visible keyboard focus and
  labels connected to fields.
- User-facing text is Persian, without demo or sample-data wording unless the
  user asks.

## Verification

Verify in proportion to the change and report real results in plain Persian:

- Template or style: render the page and check it at phone and desktop width,
  RTL, and Persian text.
- Model, form, view, or URL: `uv run python manage.py check`,
  `uv run python manage.py makemigrations --check --dry-run`,
  `uv run python manage.py test`.
- Settings or dependencies: also render the home page with Django's test
  client.
- PDF upload: try a valid PDF, a non-PDF file, and an empty form.
- AI call: automated tests use the fake module; one real call only when the
  user runs it from their own terminal with their own `.env`.
- OpenSpec files: `openspec validate --strict <change>`.
- Say plainly what you did not check.

## Definition of Done

- Behavior matches the approved scenarios, including empty and error states.
- Checks pass; migrations created and applied; no unused code.
- `AGENTS.md`, `design.md`, and `product.md` still match reality.
- The user was told in plain Persian what to open and try.

When a structural fact changes (folders, packages, commands, rules), update
this file in the same change and tell the user.
