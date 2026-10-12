"""ResumeForge backend API — FastAPI app serving the template engine.

Serves 100 resume templates: registry browsing, live rendering via
engine/renderer.py render(cfg, data), and payload validation.
"""
import json
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

log = logging.getLogger("resumeforge.api")

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent.parent          # ~/workspace/resume-forge
ENGINE_DIR = ROOT / "engine"
REGISTRY_PATH = ROOT / "templates" / "registry.json"

sys.path.insert(0, str(ENGINE_DIR))

from renderer import render          # noqa: E402
from sample_data import SAMPLES      # noqa: E402

# ---------------------------------------------------------------- registry
def load_registry():
    """Load template registry; tolerate a missing registry file."""
    if not REGISTRY_PATH.exists():
        log.warning("registry.json not found at %s — starting with an empty template list",
                    REGISTRY_PATH)
        return []
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except (json.JSONDecodeError, OSError) as exc:  # pragma: no cover
        log.warning("could not read registry.json (%s) — starting with empty list", exc)
        return []

TEMPLATES = load_registry()
BY_SLUG = {t["slug"]: t for t in TEMPLATES}

# ---------------------------------------------------------------- app
app = FastAPI(title="ResumeForge API", version="1.0.0")


# ---------------------------------------------------------------- schemas
class RenderRequest(BaseModel):
    config: dict
    data: dict


class ValidateRequest(BaseModel):
    data: dict


# ---------------------------------------------------------------- helpers
def summary(t: dict) -> dict:
    """Public list view of a template entry."""
    return {
        "slug": t.get("slug"),
        "name": t.get("name"),
        "persona": t.get("persona"),
        "tags": t.get("tags", []),
        "layout": t.get("layout"),
        "sample": t.get("sample"),
    }


def get_template(slug: str) -> dict:
    t = BY_SLUG.get(slug)
    if t is None:
        raise HTTPException(status_code=404, detail=f"unknown template slug: {slug}")
    return t


def validate_payload(data: dict) -> list:
    errors = []
    for field in ("name", "title", "email", "phone", "location", "summary"):
        val = data.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"missing or empty required field: {field}")
    exp = data.get("experience")
    if not isinstance(exp, list) or len(exp) < 1:
        errors.append("experience must be a non-empty list")
    else:
        for i, job in enumerate(exp):
            if not isinstance(job, dict):
                errors.append(f"experience[{i}] must be an object")
                continue
            for field in ("role", "company", "period"):
                if not job.get(field):
                    errors.append(f"experience[{i}] missing required field: {field}")
            bullets = job.get("bullets")
            if not isinstance(bullets, list) or not bullets:
                errors.append(f"experience[{i}] must include at least one bullet")
    edu = data.get("education")
    if not isinstance(edu, list) or len(edu) < 1:
        errors.append("education must be a non-empty list")
    skills = data.get("skills")
    if not isinstance(skills, list) or len(skills) < 1:
        errors.append("skills must be a non-empty list")
    return errors


# ---------------------------------------------------------------- routes
@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/templates")
def list_templates():
    return [summary(t) for t in TEMPLATES]


@app.get("/api/templates/{slug}")
def get_template_config(slug: str):
    return get_template(slug)


@app.get("/api/templates/{slug}/html", response_class=HTMLResponse)
def get_template_html(slug: str, sample: str = Query(default=None)):
    t = get_template(slug)
    key = sample or t.get("sample", "engineer")
    dataset = SAMPLES.get(key)
    if dataset is None:
        raise HTTPException(status_code=400,
                            detail=f"unknown sample '{key}'; valid: {sorted(SAMPLES)}")
    try:
        return render(t, dataset)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"render failed: {exc}")


@app.get("/api/samples")
def list_samples():
    return sorted(SAMPLES)


@app.get("/api/samples/{key}")
def get_sample(key: str):
    dataset = SAMPLES.get(key)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"unknown sample '{key}'")
    return dataset


@app.post("/api/render")
def render_any(req: RenderRequest):
    try:
        html = render(req.config, req.data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"render failed: {exc}")
    return JSONResponse({"html": html})


@app.post("/api/validate")
def validate(req: ValidateRequest):
    errors = validate_payload(req.data)
    return {"ok": not errors, "errors": errors}
