"""Full QA over the 100-template registry. Writes tests/QA-REPORT.md. Exit 1 on failure."""
import json, os, sys, io, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from renderer import render, full_order
from sample_data import SAMPLES
from validate_config import validate

NAMES = {"engineer": "Danish Ali", "designer": "Mahnoor Khan",
         "executive": "Kamran Shah", "general": "Areeba Tariq"}

def main():
    reg = json.load(open(os.path.join(ROOT, "docs", "registry.json")))
    fails, warns, lines = [], [], []
    lines.append(f"# QA Report — {len(reg)} templates\n")
    n_bespoke = sum(1 for c in reg if c.get("bespoke"))
    n_legacy = len(reg) - n_bespoke
    assert n_legacy == 100, f"registry has {n_legacy} legacy, want 100"

    seen, accents, displays = set(), set(), set()
    layout_n = {}
    for cfg in reg:
        slug = cfg["slug"]
        if cfg.get("bespoke"):
            fp = os.path.join(ROOT, "docs", cfg["file"])
            body = open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""
            for marker in ("window.renderResume", "DEFAULT_DATA", "photoDataUrl", "signatureDataUrl"):
                if marker not in body:
                    fails.append(f"{slug}: bespoke contract marker missing: {marker}")
            layout_n[cfg["layout"]] = layout_n.get(cfg["layout"], 0) + 1
            seen.add(slug)
            continue
        # schema
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = validate(cfg, seen)
        if not ok:
            fails.append(f"{slug}: schema invalid\n{buf.getvalue()}")
            continue
        # render
        data = SAMPLES[cfg.get("sample", "engineer")]
        try:
            html = render(cfg, data)
        except Exception as e:  # noqa
            fails.append(f"{slug}: render crashed: {e}")
            continue
        if len(html) < 8000:
            fails.append(f"{slug}: html too small ({len(html)})")
        if NAMES[cfg.get("sample", "engineer")] not in html:
            fails.append(f"{slug}: sample name missing")
        css = html.split("<style>")[1].split("</style>")[0]
        if css.count("{") != css.count("}"):
            fails.append(f"{slug}: CSS brace imbalance")
        if "{{" in html:
            fails.append(f"{slug}: unrendered template token")
        n_sec = html.count('<section class="sec">')
        # sidebar layouts render skills in sidebar, not as a section
        expect = len(full_order(cfg))
        if cfg["layout"] in ("sidebar-left", "sidebar-right"):
            expect -= 1
        if n_sec != expect:
            warns.append(f"{slug}: sections rendered {n_sec}, expected {expect}")
        accents.add(cfg["page"]["accent"].lower())
        displays.add(cfg["fonts"]["display"])
        layout_n[cfg["layout"]] = layout_n.get(cfg["layout"], 0) + 1

    lines.append(f"Unique slugs: {len(seen)}")
    lines.append(f"Distinct accent colors: {len(accents)}")
    lines.append(f"Distinct display fonts: {len(displays)}")
    lines.append(f"Layout distribution: {layout_n}\n")
    for lay, n in sorted(layout_n.items()):
        if lay != "bespoke" and not (8 <= n <= 13):
            warns.append(f"layout {lay}: count {n} outside 8-13 band")
    if warns:
        lines.append("## Warnings")
        lines.extend(f"- {w}" for w in warns)
    if fails:
        lines.append("## Failures")
        lines.extend(f"- {f}" for f in fails)
        print("\n".join(lines))
        open(os.path.join(ROOT, "tests", "QA-REPORT.md"), "w").write("\n".join(lines))
        print(f"\nQA FAILED: {len(fails)} failures, {len(warns)} warnings")
        sys.exit(1)
    lines.append(f"\nQA PASSED: {n_legacy} legacy + {n_bespoke} bespoke rendered, {len(warns)} warnings")
    open(os.path.join(ROOT, "tests", "QA-REPORT.md"), "w").write("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
