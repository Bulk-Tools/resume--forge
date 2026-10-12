"""Merge config batches -> registry.json, render all templates, stage docs/ for Pages."""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from renderer import render, LAYOUTS
from sample_data import SAMPLES
from validate_config import validate

def main():
    cfg_dir = os.path.join(ROOT, "templates", "configs")
    registry = []
    for fn in sorted(os.listdir(cfg_dir)):
        if not fn.endswith(".json"):
            continue
        items = json.load(open(os.path.join(cfg_dir, fn)))
        if isinstance(items, dict):
            items = [items]
        registry.extend(items)
    # validate all
    seen, bad = set(), 0
    for cfg in registry:
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = validate(cfg, seen)
        if not ok:
            bad += 1
            print(buf.getvalue())
    if bad:
        print(f"VALIDATION FAILED for {bad} configs — fix before rendering")
        sys.exit(1)
    # sort: layout then name for stable registry
    registry.sort(key=lambda c: (c["layout"], c["name"]))
    reg_path = os.path.join(ROOT, "docs", "registry.json")
    json.dump(registry, open(reg_path, "w"), indent=1)
    print(f"registry: {len(registry)} templates -> {reg_path}")

    # render each (build artifacts live under docs/ for GitHub Pages)
    dist = {}
    docs = os.path.join(ROOT, "docs")
    os.makedirs(os.path.join(docs, "assets"), exist_ok=True)
    dt = os.path.join(docs, "templates")
    if os.path.exists(dt):
        shutil.rmtree(dt)
    os.makedirs(dt, exist_ok=True)
    for cfg in registry:
        data = SAMPLES[cfg.get("sample", "engineer")]
        html = render(cfg, data)
        dest = os.path.join(dt, cfg["slug"])
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, "index.html"), "w").write(html)
        dist[cfg["layout"]] = dist.get(cfg["layout"], 0) + 1
    print("layout distribution:", dist)

    # stage docs/ for GitHub Pages
    shutil.copy(reg_path, os.path.join(docs, "registry.json"))
    # samples.js for the JS renderer
    js = "window.RF_SAMPLES = " + json.dumps(SAMPLES) + ";\n"
    open(os.path.join(docs, "assets", "samples.js"), "w").write(js)
    print(f"docs staged: {len(registry)} templates, registry.json, samples.js")

if __name__ == "__main__":
    main()
