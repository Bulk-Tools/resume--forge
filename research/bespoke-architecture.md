# Bespoke Template Architecture

Each template is a hand-crafted, self-contained file. No shared renderer —
the config/token engine stays for the legacy 100, but every new template is
built individually per the research concepts doc.

## File contract — `docs/templates/<slug>/index.html`

1. Single file. Inline `<style>`. Only external resource allowed: Google Fonts.
2. A4: `.page { width: 794px; min-height: 1123px; }`, `@page { size: A4; margin: 0 }`,
   `@media print` hides nothing (file IS the page).
3. Exposes `window.renderResume(data)` — rebuilds the page from data.
4. On `DOMContentLoaded`, calls `renderResume(DEFAULT_DATA)` so the file
   renders standalone (gallery iframes it directly, no JS needed from parent).
5. `DEFAULT_DATA`: compact engineer sample embedded in the file.
6. Escape all user strings (`esc()` helper). Never crash on empty fields:
   missing name → "Your Name"; empty sections → section omitted.
7. Photo: `data.photoDataUrl` → `<img>`; else initials or design-appropriate
   fallback (never an empty box).
8. Signature: `data.signatureDataUrl` → bottom-right signature block;
   absent → nothing.
9. Data shape:
   `{name,title,email,phone,location,website,linkedin,summary,
     experience:[{role,company,period,location,bullets[]}],
     education:[{degree,school,period,detail}],
     skills:[{name,level}], projects:[{name,detail}],
     certifications:[], languages:[], photoDataUrl, signatureDataUrl}`

## Registry

`docs/registry.json` entry:
`{"slug","name","persona","tags":[],"layout":"bespoke","bespoke":true,
  "file":"templates/<slug>/index.html","sample":"engineer"}`

## Consumers

- Gallery (`app.js`): `t.bespoke` → `<iframe src="t.file">`; else srcdoc render.
- Builder (`builder.js`): `current.bespoke` → `frame.src = current.file`;
  on `frame.onload` and every input → `frame.contentWindow.renderResume(data)`.
