# design.md — Persian RTL Design System (Bootstrap)

## Status

Implemented (prompt 2). The values below are what `static/css/theme.css` and
the `/design-system/` page really use. Items marked «temporary» were not
decided by the owner and were filled with a quiet neutral choice; change them
in `theme.css` and here together.

## Brand Inputs

- Product name: `جزوه‌ساز`
- Primary color: `#421454` (deep purple)
- Secondary color: `#FF5B42` (coral accent)
- Visual style: minimal, with gradients and soft tinted shadows
- Brand voice: between friendly and formal
- Corner radius: medium (`0.5rem`)
- Font: `YekanBakhFaNum` — eight weights (100, 300, 400, 600, 700, 800,
  900, 950) as `woff2` files in `static/fonts/`
- Logo: `static/brand/aleflogo.png` (square, 200×200 px), shown at 32 px in
  the navbar next to the product name, 96 px on the design-system page, and
  as the favicon.
- No dark mode (temporary: only the light theme is defined).

## Language and Direction

- `<html lang="fa" dir="rtl">`; local `bootstrap.rtl.min.css` and Bootstrap
  JS bundle.
- Logical utilities only: `ms-*`/`me-*`, `ps-*`/`pe-*`, `text-start`/
  `text-end`. Never `ml-*`, `mr-*`, `text-left`, `text-right`.
- Correct half-space (ZWNJ: «می‌شود»), Persian «ی» and «ک», Persian digits in
  product copy (the font also renders Latin digits with Persian glyphs).
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
Templates never hard-code colors; swatches on `/design-system/` read the
real computed values, so the page cannot drift from this table.

| Token | Bootstrap variable | Value |
| --- | --- | --- |
| Primary | `--bs-primary`, `--bs-primary-rgb` | `#421454`, `66, 20, 84` |
| Primary hover / active | `--jz-primary-hover`, `--jz-primary-active` | `#331040`, `#280C33` |
| Primary subtle bg / border | `--bs-primary-bg-subtle`, `--bs-primary-border-subtle` | `#F1E9F5`, `#D9C7E2` |
| Secondary | `--bs-secondary`, `--bs-secondary-rgb` | `#FF5B42`, `255, 91, 66` |
| Secondary hover / active | `--jz-secondary-hover`, `--jz-secondary-active` | `#E94A32`, `#D34029` |
| Text on secondary | `--jz-on-secondary` | `#2A0D36` (white on coral is too light for body text) |
| Success / Warning / Danger / Info | `--bs-success` … | Bootstrap defaults (`#198754`, `#FFC107`, `#DC3545`, `#0DCAF0`) — temporary |
| Page background | `--bs-body-bg` | `#FAF8FB` — temporary |
| Surface (cards) | `--jz-surface` | `#FFFFFF` |
| Text | `--bs-body-color` | `#241B2B` — temporary |
| Muted text | `--bs-secondary-color` | `#6B6373` — temporary |
| Faint text | `--bs-tertiary-color` | `#9A93A1` — temporary |
| Border | `--bs-border-color` | `#E5DFE9` — temporary |
| Headings | `--bs-heading-color` | `#280C33` |
| Link / hover | `--bs-link-color`, `--bs-link-hover-color` | primary / primary hover |
| Focus ring | `--bs-focus-ring-color` | `rgba(66, 20, 84, 0.3)`; `:focus-visible` outline 2 px primary |
| Radius | `--bs-border-radius` (`-sm`, `-lg`, `-xl`, `-xxl`) | `0.5rem` (`0.375`, `0.75`, `1`, `1.5rem`) |
| Shadows | `--bs-box-shadow-sm`, `--bs-box-shadow`, `--bs-box-shadow-lg` | purple-tinted: `--jz-shadow-sm`, `--jz-shadow`, `--jz-shadow-lg` |
| Gradients | `--jz-gradient-brand`, `--jz-gradient-accent`, `--jz-gradient-soft` | purple→violet, purple→coral, white→light purple |
| Font | `--bs-body-font-family` | `"YekanBakhFaNum", system-ui, sans-serif` |

Component variables (for example `--bs-btn-bg` on `.btn-primary`) are
overridden in `theme.css`, never inline. Extra classes defined there:
`.card-elevated`, `.bg-brand-gradient`, `.bg-accent-gradient`,
`.bg-soft-gradient`, `.brand-logo`, `.required-mark`, and the `ds-*`
helpers used only by the design-system page.

Contrast: primary on white ≈ 13:1; body text on page background ≈ 14:1;
muted text ≈ 5:1; dark text on coral ≈ 5.7:1. White text on coral is used
only for hover/active states of the secondary button, never for body copy.

## Typography

- Body 16px, line height 1.8; headings `h1`–`h6` weight 700, line height
  1.5, no skipped levels; one `h1` per page.
- Weights in use: 400 body, 600 emphasis (`fw-semibold`), 700 headings and
  buttons. 100, 300, 800, 900, 950 are loaded but reserved for display use.
- The font is loaded with `@font-face` from `static/fonts/`, using
  `font-display: swap`.

## Shape and Spacing

- Bootstrap spacing scale (`p-3`, `gap-3`, `mb-4`); content in `.container`.
- Shadows only on overlays, the navbar, and raised cards (`.card-elevated`,
  `shadow-sm`). Gradients only on hero blocks and highlighted stat cards,
  never behind running text.

## Components

Bootstrap markup; shared pieces in `templates/components/`:

| Partial | Parameters | Use |
| --- | --- | --- |
| `alert.html` | `kind`, `message`, `dismissible`, `title` | Django messages and inline notices |
| `card.html` | `title`, `text`, `badge`, `badge_kind`, `action_url`, `action_label`, `elevated` | one item in a grid |
| `form-field.html` | `field`, `help`, `show_valid` | label, «(الزامی)» marker, help, error under the field; needs `{% load form_extras %}` |
| `empty-state.html` | `title`, `text`, `action_url`, `action_label` | empty lists with one next action |
| `pagination.html` | `page_obj`, `anchor` | long lists; hides itself for one page |
| `confirm-modal.html` | `modal_id`, `item_name`, `action_url`, `text` (optional body, default «این کار قابل بازگشت نیست.»), `demo` | delete confirmation, POST with CSRF |
| `page-header.html` | `title`, `lead`, `breadcrumbs`, `action_url`, `action_label` | top of every page |

- **Buttons:** one primary per view; destructive = `btn-danger` + confirm.
- **Forms:** visible `<label>`, optional help text, error under the field
  (`invalid-feedback`), required marked in words; widgets get
  `form-control`/`form-select`/`form-check-input` classes in the Django
  form, `is-invalid`/`is-valid` via the `add_class` filter.
- **Feedback:** alerts from Django messages; friendly empty state with one
  next action; toasts live in the `toasts` block of `base.html`.
- **Navigation:** navbar collapses on phone; active page marked; pagination
  for long lists.
- **Overlays:** modal for confirmations; Escape closes; tooltips enabled by
  `static/js/app.js`.
- **Data:** cards for items, tables in `.table-responsive`, list groups.

## Microcopy

- Buttons say what they do: «ذخیره»، «افزودن»، «حذف».
- Errors say what went wrong and how to fix it, without blame.
- Confirmations name the item: ««X» حذف شود؟».
- Voice: between friendly and formal; no slang, no stiff bureaucratic forms.

## The `/design-system/` Page

`core/templates/core/design-system.html` with one partial per section in
`core/templates/core/design-system/`. A section index sits at the side
(sticky on desktop, on top on phone). Each section has a title, one line on
when to use it, and examples in every state:

- **Brand:** logo, product name, all eight font weights, brand gradient.
- **Colors:** swatches with Persian name, computed value, and usage; status
  colors; text and border grays.
- **Typography:** `h1`–`h6`, lead, body, small, muted, link, Persian digits,
  LTR text, lists, quote.
- **Buttons:** primary, secondary, outline, success, danger, link; three
  sizes; disabled; loading; button group; full width on phone.
- **Forms:** complete sample form through `form-field.html`, error state
  from a bound invalid form, valid/disabled/read-only, checkbox, radio,
  switch, range, date, input group, floating label, dropdown.
- **Feedback:** alerts (4 kinds, dismissible), badges, toast, progress,
  spinners, empty state, loading placeholder.
- **Navigation:** navbar, breadcrumb, tabs, pills, working pagination.
- **Overlays:** dropdown menu, confirm modal, tooltip.
- **Data:** card, stat cards, table with status badges, list group,
  accordion.

When a token, component, or wording rule changes in code, update this file and
`/design-system/` in the same change.
