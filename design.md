# design.md — Persian RTL Design System (Bootstrap)

## Status

Template. Prompt 1 (documents + Django base) fills only the product name and
uses a neutral `system-ui` fallback. After the owner places the font in
`static/fonts/` and the logo in `static/brand/`, prompt 2 fills the brand
inputs, writes the tokens into `static/css/theme.css`, and builds the
`/design-system/` page. After that this file must describe what is really
implemented.

## Brand Inputs

- Product name: `جزوه‌ساز`
- Primary color: `[add, e.g. #0F2A5F]`
- Secondary color: `[add]`
- Visual style (3–6 words): `[add, e.g. calm, clean, trustworthy]`
- Brand voice (2–3 words): `[add, e.g. friendly, clear]`
- Font: `[font name]` — files placed by the user in `static/fonts/`
- Logo (optional): `static/brand/[file name]`

If an input is missing, use a quiet neutral fallback and record it here as
«temporary». Do not invent brand history or positioning.

## Language and Direction

- `<html lang="fa" dir="rtl">`; local `bootstrap.rtl.min.css` and Bootstrap
  JS bundle.
- Logical utilities only: `ms-*`/`me-*`, `ps-*`/`pe-*`, `text-start`/
  `text-end`. Never `ml-*`, `mr-*`, `text-left`, `text-right`.
- Correct half-space (ZWNJ: «می‌شود»), Persian «ی» and «ک», Persian digits in
  product copy.
- Latin text, email, URL, phone, and code sit in `dir="ltr"` or `<bdi>`.

## Principles

1. Clear before decorative.
2. Consistent before novel: Bootstrap components and these tokens.
3. Calm density.
4. Persian-first typography: comfortable line height.
5. Visible states: hover, focus, disabled, empty, error.
6. One primary action per view.

## Tokens

CSS variables in `static/css/theme.css` override Bootstrap's variables.
Templates never hard-code colors.

| Token | Bootstrap variable | Value |
| --- | --- | --- |
| Primary | `--bs-primary`, `--bs-primary-rgb` | `[add]` |
| Secondary | `--bs-secondary`, `--bs-secondary-rgb` | `[add]` |
| Success | `--bs-success` | Bootstrap default |
| Warning | `--bs-warning` | Bootstrap default |
| Danger | `--bs-danger` | Bootstrap default |
| Page background | `--bs-body-bg` | `[add]` |
| Text | `--bs-body-color` | `[add]` |
| Muted text | `--bs-secondary-color` | `[add]` |
| Border | `--bs-border-color` | `[add]` |
| Link | `--bs-link-color` | primary |
| Radius | `--bs-border-radius` | `[add, e.g. 0.5rem]` |
| Font | `--bs-body-font-family` | `[font], system-ui, sans-serif` |

Text/background pairs need comfortable contrast. Component variables (for
example `--bs-btn-bg` on `.btn-primary`) are overridden in `theme.css`, never
inline.

## Typography

- Body 16px, line height about 1.8; headings `h1`–`h6` heavier, no skipped
  levels; one `h1` per page.
- The font is loaded with `@font-face` from `static/fonts/`, using
  `font-display: swap`.

## Shape and Spacing

- Bootstrap spacing scale (`p-3`, `gap-3`, `mb-4`); content in `.container`.
- Shadows only on overlays and raised cards (`shadow-sm`).

## Components

Bootstrap markup; shared pieces in `templates/components/`.

- **Buttons:** one primary per view; destructive = `btn-danger` + confirm.
- **Forms:** visible `<label>`, optional help text, error under the field
  (`invalid-feedback`), required marked in words.
- **Feedback:** alerts from Django messages; friendly empty state with one
  next action.
- **Navigation:** navbar collapses on phone; active page marked; pagination
  for long lists.
- **Overlays:** modal for confirmations; Escape closes.
- **Data:** cards for items, tables in `.table-responsive`, list groups.

## Microcopy

- Buttons say what they do: «ذخیره»، «افزودن»، «حذف».
- Errors say what went wrong and how to fix it, without blame.
- Confirmations name the item: ««X» حذف شود؟».

## The `/design-system/` Page

A professional UI kit page in Persian with a section index (sticky on
desktop). Each section has a title, one line on when to use it, and examples
in every state (default, hover, focus, disabled, error):

- **Brand:** logo, product name, font and its weights.
- **Colors:** swatches with Persian name, value, and usage; status colors;
  text and border grays.
- **Typography:** `h1`–`h6`, lead, body, small, muted, link, lists, quote,
  LTR text, Persian digits.
- **Buttons:** primary, secondary, outline, success, danger, link; three
  sizes; disabled; loading; button group; full width on phone.
- **Forms:** text, email/number (LTR), textarea, select, checkbox, radio,
  switch, date, range, input group, floating label, help text, valid and
  invalid, disabled, read-only, and one complete example form.
- **Feedback:** alerts (4 kinds, dismissible), badges, toast, progress,
  spinner, empty state, loading placeholder.
- **Navigation:** navbar, breadcrumb, tabs, pills, pagination.
- **Overlays:** dropdown menu, confirm modal, tooltip.
- **Data:** card, stat card, table with status badges, list group, accordion.

Shared partials: `alert`, `card`, `form-field`, `empty-state`, `pagination`,
`confirm-modal`, `page-header` in `templates/components/`.

When a token, component, or wording rule changes in code, update this file and
`/design-system/` in the same change.
