"""API tests for the ResumeForge backend — uses fastapi TestClient."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from main import app, summary

client = TestClient(app)

# ---------------------------------------------------------------- mock configs
# Minimal-but-valid per DESIGN-SYSTEM.md (page + sidebar palettes, fonts,
# header, section titles, skills, experience, sections order, accents, density).

CLASSIC_CFG = {
    "slug": "test-classic", "name": "Test Classic", "persona": "Test Engineer",
    "sample": "engineer", "tags": ["modern", "ats-friendly"],
    "layout": "classic",
    "page": {"bg": "#FFFFFF", "ink": "#1B1B1B", "muted": "#6E6E6E",
             "accent": "#0B5FFF", "accent2": "#00C2A8", "rule": "#E4E4E4"},
    "sidebar": {"bg": "#0B1F3A", "ink": "#FFFFFF", "muted": "#B9C4D6", "accent": "#00C2A8"},
    "fonts": {"display": "Sora", "body": "Inter"},
    "header": {"align": "left", "photo": "none", "name_size": 34, "title_rule": "full-rule"},
    "section_title": {"style": "rule", "case": "upper", "tracking": "0.22em", "size": 12},
    "skills": {"style": "chips"},
    "experience": {"style": "standard"},
    "sections": {"order": ["summary", "experience", "skills", "education"]},
    "accents": {"page_shape": "none", "marker": "dash"},
    "density": "comfortable",
}

SIDEBAR_CFG = {
    **CLASSIC_CFG,
    "slug": "test-sidebar", "name": "Test Sidebar",
    "layout": "sidebar-left",
    "page": {"bg": "#FFFFFF", "ink": "#14342B", "muted": "#5F7A6F",
             "accent": "#14532D", "accent2": "#D4A017", "rule": "#DCE7E1"},
    "fonts": {"display": "Fraunces", "body": "Public Sans"},
    "header": {"align": "center", "photo": "circle", "name_size": 30, "title_rule": "accent-bar"},
    "section_title": {"style": "sideline", "case": "title", "tracking": "0.10em", "size": 13},
    "skills": {"style": "bars"},
    "experience": {"style": "card"},
}

GOOD_DATA = {
    "name": "Test Candidate",
    "title": "QA Engineer",
    "email": "test@example.com",
    "phone": "+1 555 0100",
    "location": "Test City",
    "website": "testcandidate.dev",
    "linkedin": "linkedin.com/in/testcandidate",
    "summary": "A test summary.",
    "experience": [{"role": "QA Engineer", "company": "TestCo", "location": "Test City",
                    "period": "2020 — 2024", "bullets": ["Did testing."]}],
    "education": [{"degree": "BS CS", "school": "Test University", "period": "2016 — 2020"}],
    "skills": [{"name": "Testing", "level": 90}],
    "languages": [{"name": "English", "level": "Native"}],
    "projects": [{"name": "Test Suite", "detail": "Built a test suite."}],
    "certifications": [{"name": "ISTQB Foundation", "detail": "2021"}],
}

BAD_DATA = {k: v for k, v in GOOD_DATA.items() if k != "email"}


def run_tests():
    passed = failed = 0

    def check(label, cond, extra=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  PASS  {label}")
        else:
            failed += 1
            print(f"  FAIL  {label} {extra}")

    print("== health ==")
    r = client.get("/health")
    check("GET /health 200", r.status_code == 200, r.text)
    check("GET /health body", r.json() == {"ok": True})

    print("== templates ==")
    r = client.get("/api/templates")
    check("GET /api/templates 200", r.status_code == 200, r.text)
    check("GET /api/templates returns a list", isinstance(r.json(), list))
    if isinstance(r.json(), list) and r.json():
        keys = set(r.json()[0].keys())
        check("template summary shape",
              keys == {"slug", "name", "persona", "tags", "layout", "sample"}, str(keys))
    r = client.get("/api/templates/does-not-exist")
    check("GET /api/templates/{slug} 404 on unknown", r.status_code == 404)

    print("== samples ==")
    r = client.get("/api/samples")
    check("GET /api/samples 200", r.status_code == 200)
    check("GET /api/samples lists the 4 keys",
          set(r.json()) == {"engineer", "designer", "executive", "general"})
    r = client.get("/api/samples/engineer")
    check("GET /api/samples/engineer has name",
          r.status_code == 200 and r.json().get("name") == "Danish Ali")
    r = client.get("/api/samples/nope")
    check("GET /api/samples/nope 404", r.status_code == 404)

    print("== render ==")
    for label, cfg in (("classic", CLASSIC_CFG), ("sidebar-left", SIDEBAR_CFG)):
        r = client.post("/api/render", json={"config": cfg, "data": GOOD_DATA})
        check(f"POST /api/render ({label}) 200", r.status_code == 200, r.text[:200])
        html = r.json().get("html", "") if r.status_code == 200 else ""
        check(f"POST /api/render ({label}) html contains name",
              "Test Candidate" in html, html[:120])
    r = client.post("/api/render", json={"config": {"layout": "bogus"}, "data": {}})
    check("POST /api/render 422 on bad config", r.status_code == 422)

    print("== validate ==")
    r = client.post("/api/validate", json={"data": GOOD_DATA})
    check("POST /api/validate good payload ok:true",
          r.status_code == 200 and r.json() == {"ok": True, "errors": []}, r.text)
    r = client.post("/api/validate", json={"data": BAD_DATA})
    body = r.json() if r.status_code == 200 else {}
    check("POST /api/validate missing email -> ok:false",
          r.status_code == 200 and body.get("ok") is False
          and any("email" in e for e in body.get("errors", [])), r.text)
    r = client.post("/api/validate", json={"data": {}})
    body = r.json() if r.status_code == 200 else {}
    check("POST /api/validate empty payload -> errors",
          r.status_code == 200 and body.get("ok") is False
          and len(body.get("errors", [])) >= 9, r.text)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_tests())
