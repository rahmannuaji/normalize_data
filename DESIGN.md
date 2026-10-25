---
name: Normalin
description: "Datamu tidak normal? Tenang, ada jalannya."
colors:
  indigo: "#3B5BDB"
  indigo-dark: "#2F49B0"
  indigo-soft: "#E8EDFF"
  background: "#F6F7FB"
  surface: "#FFFFFF"
  surface-sunken: "#F3F5FA"
  ink: "#1B2333"
  muted: "#5D6779"
  line: "#E3E7EF"
  ok: "#22702F"
  ok-soft: "#E6F6EA"
  warn: "#8A5200"
  warn-soft: "#FFF4DD"
  bad: "#C92A2A"
  bad-soft: "#FDE8E8"
  info: "#24398F"
typography:
  display:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "44px"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.35
  body:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
  small:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.4
  report:
    fontFamily: "'Times New Roman', Times, serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  btn: "10px"
  card: "14px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.indigo}"
    textColor: "{colors.surface}"
    rounded: "{rounded.btn}"
    padding: "10px 18px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.indigo-dark}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.btn}"
    padding: "10px 18px"
    height: "44px"
  button-secondary-hover:
    backgroundColor: "{colors.surface-sunken}"
  button-small:
    rounded: "{rounded.btn}"
    padding: "6px 12px"
    height: "32px"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.card}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.btn}"
    padding: "8px 12px"
    height: "44px"
  step-active:
    backgroundColor: "{colors.indigo-soft}"
    textColor: "{colors.indigo}"
    rounded: "{rounded.btn}"
    height: "44px"
  option-selected:
    backgroundColor: "{colors.indigo-soft}"
    rounded: "{rounded.card}"
    padding: "{spacing.md}"
  pill-ok:
    backgroundColor: "{colors.ok-soft}"
    textColor: "{colors.ok}"
    rounded: "{rounded.pill}"
    padding: "3px 9px"
  pill-warn:
    backgroundColor: "{colors.warn-soft}"
    textColor: "{colors.warn}"
    rounded: "{rounded.pill}"
    padding: "3px 9px"
  pill-bad:
    backgroundColor: "{colors.bad-soft}"
    textColor: "{colors.bad}"
    rounded: "{rounded.pill}"
    padding: "3px 9px"
  note-info:
    backgroundColor: "{colors.indigo-soft}"
    textColor: "{colors.info}"
    rounded: "{rounded.btn}"
    padding: "12px 14px"
---

# Design System: Normalin

## Overview

**Creative North Star: "Meja Konsultasi yang Tenang"**

Normalin is a quiet statistics consulting desk for undergraduates whose normality test came back "not normal". The shipped build is a restrained light-only product UI: a cool blue-grey page, white cards with hairline borders, and one indigo accent reserved for action, focus, links and the active step. Results read as a traceable diagnosis (status, cause, labelled remedy, copyable report), not a wall of SPSS output. The home screen is a short door into the tool (Operate mode), not a marketing page.

Density is moderate and steady: a single 1040px column, 16 to 24px gaps, 44px touch targets. The only place the system changes register is the report preview, which switches to Times New Roman on white so it looks like a thesis page and can be printed or pasted into a Chapter IV.

**Key Characteristics:**
- Restrained palette: neutral blue-tinted ground, one indigo accent, status colors used only for status.
- Every status is text + soft background + Lucide icon, never color alone.
- Flat, border-defined surfaces; shadow appears once (active tab).
- Plus Jakarta Sans throughout, tabular numerals in tables; Times New Roman only inside the report.
- Calm motion: 250ms fade and 6px rise on step change; everything switches off under reduced motion.

## Colors

A cool, near-white neutral field with one saturated indigo and a four-state status family. Light mode only (`color-scheme: light`), because users work beside Word/SPSS and paste results into white documents.

### Primary
- **Indigo** (#3B5BDB): primary buttons, links, focus ring, active step, selected option border, upload icon, chart bars (at 55% opacity), checkbox accent, caret.
- **Indigo Dark** (#2F49B0): hover and pressed state of primary button and links.
- **Indigo Soft** (#E8EDFF): active step, selected option/chip, info note, loading bar, text selection, editable-cell focus.

### Neutral
- **Background** (#F6F7FB): page ground.
- **Surface** (#FFFFFF): header, cards, tables, inputs, report page.
- **Surface Sunken** (#F3F5FA): table headers, drop zone, skipped status, hover for secondary button and step.
- **Ink** (#1B2333): headings, body text, normal-curve line, APA table rules.
- **Muted** (#5D6779): captions, labels, secondary copy, inactive step.
- **Line** (#E3E7EF): every card, table, input and divider border; inactive step number disc; tab-bar track.

### Status (always paired with a soft background and an icon)
- **OK** (#22702F) on **OK Soft** (#E6F6EA): normal, recommended, privacy pill, completed step.
- **Warn** (#8A5200) on **Warn Soft** (#FFF4DD): slight deviation, "acceptable with a note", reviewed chips.
- **Bad** (#C92A2A) on **Bad Soft** (#FDE8E8): not normal, flagged cells, suspect chips, tail bars and Q-Q points, error bar.
- **Info** (#24398F) on Indigo Soft: explanatory notes and the loading bar.

### Named Rules
**The One Indigo Rule.** Indigo means "you can act here or you are here". It never marks status and never decorates.
**The Status Triplet Rule.** A status is always soft background + dark text color + icon + word. Color alone never carries meaning.
**The Light Paper Rule.** No dark mode, no gradients, no glass. Surfaces are white on a pale blue-grey ground.

## Typography

**Display / Heading / Body Font:** Plus Jakarta Sans (Google Fonts, weights 400 to 800; fallback system-ui, -apple-system, Segoe UI, sans-serif)
**Report Font:** Times New Roman (Times, serif), only in the report preview and APA table
**Mono:** a `--font-mono` stack is declared but not used by any shipped rule.

**Character:** A friendly geometric sans with a heavy 800 headline for warmth, contrasted by a serif academic page for the output. Numbers are tabular so digits align in every table.

### Hierarchy
- **Display** (800, 44px, 1.15, -0.02em; 30px under 760px): home H1 only; second line in Indigo via an accent span.
- **Headline** (700, 24px, 1.25, -0.01em; 22px under 760px): step titles (focused programmatically, no outline).
- **Title** (700, 16px, 1.35): card and finding headings; feature headings on the home page.
- **Body** (400, 16px, 1.55): default text; `.sub` lead paragraphs capped at 65ch.
- **Small** (400, 14px, 1.5): notes, table cells, option descriptions.
- **Label** (500 to 600, 13px): step labels, captions, chips, header privacy pill, footer. Smallest text is 12px (pill, step number, chart ticks). No uppercase or letter-spaced micro-labels exist.
- **Report** (Times New Roman 400, 16px, 1.7): report paragraphs; APA table at 16px, 14px under 480px.

### Named Rules
**The Tabular Rule.** Tables use `tabular-nums`; statistics never sit in proportional digits.
**The Thesis Page Rule.** Serif appears only where the output imitates a thesis page.

## Layout

One centered column, `max-width: 1040px`, 16px side padding, main padding 32px top / 64px bottom (24px top under 760px). Pages are shown one at a time inside a 7-step wizard; the header is sticky and holds the logo (left), the privacy pill (right) and a horizontally scrolling numbered stepper with edge-fade mask.

Home hero is a 1.2fr / 1fr grid (28px gap): copy and two buttons left, sample histogram card right; it collapses to one column under 760px with the chart below the buttons. Card groups use auto-fit grids (`minmax(min(280px,100%),1fr)` for two-up, 220px for three-up, 240px for comparisons) with 16px gaps. Spacing scale is 4 / 8 / 16 / 24 / 32 / 48px; several one-off values (10, 12, 14, 18, 28, 36, 64px) also appear in components. Breakpoints: 760px (hero, type), 480px (solution header wraps, tests table becomes stacked rows, APA table tightens), 420px (smaller logo and privacy pill). Wide tables scroll inside a bordered wrapper. Print hides header, footer, navigation and actions and prints the report on white.

## Elevation & Depth

Flat and border-defined. Depth comes from white cards on the tinted ground and 1px Line borders. The single shadow is `--shadow-sm` (`0 1px 3px` of Ink at 10%) on the active tab in a segmented control. Hover never lifts; it shifts border or background tone.

### Named Rules
**The Flat Card Rule.** Cards, notes and status blocks carry no shadow. Use a border and a tone change.

## Shapes

Soft but not bubbly. Buttons, inputs, notes, tables, details and the step buttons use 10px; cards, options, drop zone and status blocks use 14px; pills and chips are full capsules (9999px); step numbers and solution rank badges are circles. The logo mark is a 28px indigo rounded square (8px) holding a white bell-curve stroke. Drop zone uses a 2px dashed indigo-tinted border. Table headers use Surface Sunken; flagged cells use Bad Soft with bold Bad text.

## Components

### Buttons
- **Shape:** 10px radius, 44px min height, 10px 18px padding, 600 weight 15px text.
- **Primary:** Indigo fill, white text; hover/active Indigo Dark.
- **Secondary (default):** white fill, Line border, Ink text; hover tints the border toward indigo and fills Surface Sunken.
- **Small:** 32px height, 6px 12px padding, 13px text, with an invisible pseudo-element extending the touch area to 44px.
- **Disabled:** 50% opacity, not-allowed cursor, hover colors unchanged.
- **Focus:** global 2px Indigo outline, 2px offset.

### Stepper
Numbered row of 44px buttons with a 22px number disc. Inactive: Muted on Line disc; done: OK disc with white number; active: Indigo Soft background, Indigo text, 600 weight, Indigo disc; locked steps are 55% opacity.

### Cards / Containers
White, 14px radius, 1px Line border, 24px padding. `flush` variant removes padding for lists of findings. Selection cards (`opt`) are 1.5px bordered buttons with a 24px indigo icon, turning Indigo border + Indigo Soft on selection; disabled options go sunken and Muted with a Warn explanatory line.

### Inputs / Fields
44px tall, 10px radius, Line border, white fill, 14px label above at weight 500 with 4px gap; hover tints the border toward indigo; focus uses the global outline. Table cells can be contenteditable and take an Indigo Soft background on focus. Checkboxes are 20px with Indigo accent. The drop zone is a dashed, sunken, centered target with a 34px indigo upload icon and a focus-within ring.

### Chips and Pills
Chips (13px, 36px high, capsule, Line border) represent items; reviewed state uses Warn, suspect state uses Bad, selected uses Indigo. Pills (12px bold, capsule) are non-interactive status labels in ok / warn / bad / info / skipped, always with a 14px icon.

### Notes and Status Blocks
Notes: 10px radius, icon + text, ok / warn / info / bad variants on soft backgrounds. Status blocks: 14px radius, 18px padding, tinted border (status color at 30%), 20px 800-weight headline with icon, and a skipped variant in sunken grey.

### Tabs and Disclosure
Segmented tab bar: Line track, 12px radius, white active tab with `--shadow-sm`. `details`/summary and solution accordions are bordered, 44px headers with a chevron that rotates 180deg over 200ms.

### Tables
14px tabular text, Surface Sunken 13px Muted headers, Line row dividers, no wrap with horizontal scroll. Under 480px the tests table restacks into flex rows with data labels. The APA table is a separate form: no fill, 2px Ink top and bottom rules, serif.

### Charts (Plotly, charts.js and hero SVG)
Bars Indigo at 55% opacity, normal curve Ink 2px, tail bars and flagged Q-Q points Bad; transparent paper; axis Line 1.5px. Clicking a Q-Q point names the respondent row.

### Icons
Lucide outline set (24px grid, 2px stroke, `currentColor`) as an SVG `<symbol>` sprite at `web/assets/icons.svg`, referenced via `<svg class="ic"><use href="assets/icons.svg#name"/></svg>`. Default size 1.25em; scaled per context (14px pill, 16px privacy, 22 to 34px feature and drop). Names in use: upload, keyboard, flask-conical, lock, arrow-right, arrow-left, circle-check, triangle-alert, circle-x, circle-slash, circle-help, info, link, trending-up, scale, repeat, puzzle, search, file-spreadsheet, rotate-ccw, copy, download, printer, ban, chevron-down, plus.

### Motion
- Page change: opacity 0 to 1 and 6px rise, 250ms, `cubic-bezier(.16, 1, .3, 1)`.
- Hover/color transitions: 150ms; chevron rotation: 200ms.
- Loading bar: 2px indigo segment sliding across the info strip, 1.6s infinite.
- `prefers-reduced-motion: reduce` sets all animation and transition to none and scroll-behavior to auto.

### Logo
`web/assets/logo.svg`: indigo rounded-square mark with a white bell curve plus "Normalin" wordmark (800, -0.02em, Ink); 136x28 in the header, 112x23 under 420px. `favicon.svg` is the mark alone.

## Do's and Don'ts

### Do:
- **Do** take every color, radius, space and font from the `:root` tokens in `web/style.css`.
- **Do** pair every status with its soft background, dark text color, Lucide icon and a word.
- **Do** keep touch targets at 44px minimum, extending small controls with a pseudo-element.
- **Do** keep indigo for actions, focus, links and the active step only.
- **Do** write in Indonesian with "kamu", short and calm; explain statistical terms in plain words.
- **Do** keep cards flat: 1px Line border, no shadow.
- **Do** use tabular numerals for statistics and the serif face only inside the report.
- **Do** honor `prefers-reduced-motion` for any new animation.

### Don't:
- **Don't** use emoji, gradients, glass or dark surfaces.
- **Don't** introduce a second accent hue or use status colors as decoration.
- **Don't** distinguish states by color alone.
- **Don't** add a shadow to resting cards or lift them on hover.
- **Don't** use "menormalkan data" or promise normality; remedies are labelled with what they change in interpretation.
- **Don't** use text smaller than 12px.
- **Not canonized (defects the build carries):** a few one-off radii (12px tab track, 9px tab) and off-scale paddings are build residue, not rules for new surfaces.
