# ResumeForge

100 premium resume templates with a live gallery, an interactive resume builder, and a backend API — all in one private repo.

## What's inside

| Path | What it is |
|---|---|
| `docs/` | Live website (GitHub Pages): template gallery + resume builder. Start at `docs/index.html`. |
| `docs/templates/<slug>/` | 100 rendered, standalone A4 resume templates (open any `index.html` directly). |
| `docs/registry.json` | Machine-readable catalog of all 100 templates. |
| `templates/configs/` | The 100 template design configs (JSON) — the source of truth. |
| `templates/registry.json` | Merged + validated registry. |
| `engine/` | Python renderer: config JSON → standalone A4 HTML resume. 10 layout families, 6 section-title styles, 6 skills styles, SVG page accents. |
| `api/` | FastAPI backend: template catalog, on-demand HTML rendering, resume-data validation. See `api/README.md`. |
| `tests/` | `qa.py` — renders and validates all 100 templates; `QA-REPORT.md` is its output. |
| `DESIGN-SYSTEM.md` | The design contract every template follows. |

## Prerequisites

- Python 3.10+ (engine, QA, API)
- Node 18+ (only if you want to run the site's JS renderer tests)
- For the API: `pip install -r api/requirements.txt` (or use `api/Dockerfile`)

No build step for the website — it's static. Serve `docs/` with any static server or enable GitHub Pages on the `docs/` folder.

## Regenerate everything

```bash
cd engine
python3 render_all.py   # validate configs -> registry.json -> render 100 templates -> stage docs/
cd ..
python3 tests/qa.py     # full QA, writes tests/QA-REPORT.md
```

## API quick start

```bash
cd api && pip install -r requirements.txt
uvicorn main:app --reload
# GET http://127.0.0.1:8000/api/templates
```

## Design notes

Every template is a curated design config (palette, font pairing, layout, section styles, accents) rendered by one engine — see `DESIGN-SYSTEM.md` for the anti-generic rules each template was held to.
