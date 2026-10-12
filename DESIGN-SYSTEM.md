# ResumeForge — Design System Spec (v1)

Contract for all 100 template configs. The renderer (`engine/renderer.py`) turns each
config + sample dataset into a standalone A4 HTML resume. The gallery/builder read
`templates/registry.json`.

## Config schema (JSON, one object per template)

```json
{
  "slug": "kebab-case-unique",
  "name": "Human Name",
  "persona": "Target role, e.g. Senior Backend Engineer",
  "sample": "engineer | designer | executive | general",
  "tags": ["modern", "ats-friendly"],
  "layout": "classic | sidebar-left | sidebar-right | banner | timeline | editorial | cards | swiss | creative | compact",
  "page":   {"bg":"#FFFFFF","ink":"#1B1B1B","muted":"#6E6E6E","accent":"#0B5FFF","accent2":"#00C2A8","rule":"#E4E4E4"},
  "sidebar":{"bg":"#0B1F3A","ink":"#FFFFFF","muted":"#B9C4D6","accent":"#00C2A8"},
  "fonts": {"display": "Sora", "body": "Inter"},
  "header": {"align": "left|center|right", "photo": "none|circle|rounded|square", "name_size": 34, "title_rule": "none|accent-bar|full-rule"},
  "section_title": {"style": "rule|boxed|band|numbered|plain|sideline", "case": "upper|title", "tracking": "0.22em", "size": 12},
  "skills": {"style": "bars|chips|dots|columns|levels|list"},
  "experience": {"style": "standard|timeline|card"},
  "sections": {"order": ["summary","experience","skills","education","projects","certifications","languages"]},
  "accents": {"page_shape": "none|diagonal|wave|arch|corners|dots", "marker": "dash|square|dot|chevron|none"},
  "density": "comfortable|compact"
}
```

Rules:
- `sidebar` is required only for `sidebar-left` / `sidebar-right` layouts (ignored otherwise, but include it anyway).
- `layout: timeline` forces `experience.style: timeline`. Other layouts may use any experience style.
- `sections.order` must start with `summary` and include `experience`, `skills`, `education`. Max 7 entries.
- All colors are 6-digit hex. `ink` on `bg` and `sidebar.ink` on `sidebar.bg` must pass a basic contrast check (QA enforces ratio >= 3.0 for large text usage).
- Fonts must come from the allowlist below. `display` != `body` is encouraged; never use the same font for both unless the design concept demands it.
- `photo: none` is valid and encouraged for ATS-friendly templates (roughly 40% of the set should have no photo).

## Font allowlist (Google Fonts — renderer builds the <link> automatically)

Serif/display: Playfair Display, DM Serif Display, Fraunces, Libre Baskerville,
Merriweather, Lora, Cormorant Garamond, EB Garamond, Noto Serif, PT Serif,
Source Serif 4, Crimson Pro, Spectral, Bitter, Roboto Slab, Zilla Slab, Arvo
Sans: Inter, Source Sans 3, Open Sans, Roboto, Lato, Montserrat, Poppins,
Raleway, Nunito, Work Sans, DM Sans, Manrope, Outfit, Jost, Archivo,
Space Grotesk, Sora, Lexend, Plus Jakarta Sans, Public Sans, Barlow, Fira Sans,
Karla, Mulish, Heebo, Rubik, Cabin, PT Sans, Noto Sans, Exo 2, Titillium Web,
Ubuntu, Varela Round
Condensed/impact: Oswald, Bebas Neue, Anton, Roboto Condensed, Barlow Condensed,
Archivo Black, Josefin Sans, Quicksand
Mono: JetBrains Mono, Fira Code, Source Code Pro, IBM Plex Mono, Space Mono

## Anti-generic rules (from the design skills — non-negotiable)

1. No template may use Inter + slate/gray as its whole identity. If `body` is Inter,
   the display font, palette and layout must carry a strong point of view.
2. Each template gets ONE memorable element (a diagonal band, a huge index number,
   an arch photo, a duotone sidebar, a timeline rail…) — everything else stays quiet.
3. Banned defaults: cream #F4F1EA + terracotta; near-black + acid-green; all-caps
   tracked eyebrow above every heading; identical rounded cards with soft shadows;
   "WORD — fragment" labels; middle-dot meta strings.
4. Typography must be deliberate: display/body pairings should feel chosen for the
   persona (e.g. a lawyer gets a stately serif; a game developer gets something
   with energy; a nurse gets warmth, not cold tech).
5. Palettes must be real color systems (4-6 named roles filled with intent), not
   "blue accent on white" × 100. Use deep greens, oxblood, ink navy, warm ochre,
   teal/graphite, plum, copper, forest, slate-blue duotones, etc. Vary widely.
6. Vary `section_title.style`, `skills.style`, `accents.marker`, `header.align`
   across the set — the QA report flags overused combos.

## Layout families (10 — each used 8-12 times across the 100)

- classic: centered or left header, single column, hairline rules. The "safe" family — make each one earn it with type + color.
- sidebar-left / sidebar-right: sidebar holds photo, contact, skills, languages; main column holds summary, experience, education.
- banner: full-width accent banner header (name reversed out), content below in 1-2 columns.
- timeline: experience rendered on a vertical rail with dots/dates; strong for careers with progression.
- editorial: magazine rhythm — big serif name, drop-cap-ish summary, two-column body text for experience.
- cards: projects/skills as bordered cards; good for creatives and engineers.
- swiss: grid, huge whitespace, tiny tracked labels, hairlines. Restraint as luxury.
- creative: oversized display type, color blocks, geometric shapes. For designers, marketers, media.
- compact: dense one-pager, small type, maximum information fit. For ATS + long careers.

## Sample datasets (`engine/sample_data.py`)

- engineer: "Danish Ali" — Senior Backend Engineer
- designer: "Mahnoor Khan" — Product Designer
- executive: "Kamran Shah" — Chief Operations Officer
- general: "Areeba Tariq" — Marketing Manager
Set `sample` to the closest dataset for the persona.

## Tags (filter facets in the gallery)

Style: modern, classic, minimal, creative, elegant, bold
Structure: ats-friendly, one-page, two-column, with-photo
Audience: executive, tech, design, healthcare, education, legal, finance, trades, student
Pick 3-5 per template. `ats-friendly` only when layout is classic/compact/swiss AND photo is none.
