"""Validate template config files against DESIGN-SYSTEM.md. Usage: validate_config.py <file.json>"""
import json, re, sys

FONTS = """Playfair Display DM Serif Display Fraunces Libre Baskerville Merriweather Lora Cormorant Garamond
EB Garamond Noto Serif PT Serif Source Serif 4 Crimson Pro Spectral Bitter Roboto Slab Zilla Slab Arvo
Inter Source Sans 3 Open Sans Roboto Lato Montserrat Poppins Raleway Nunito Work Sans DM Sans Manrope Outfit
Jost Archivo Space Grotesk Sora Lexend Plus Jakarta Sans Public Sans Barlow Fira Sans Karla Mulish Heebo Rubik
Cabin PT Sans Noto Sans Exo 2 Titillium Web Ubuntu Varela Round Oswald Bebas Neue Anton Roboto Condensed
Barlow Condensed Archivo Black Josefin Sans Quicksand JetBrains Mono Fira Code Source Code Pro IBM Plex Mono Space Mono""".split("\n")
FONTS = [f.strip() for f in " ".join(FONTS).split("  ") if f.strip()]
# normalize: split on 2+ spaces failed; build properly:
FONTS = ["Playfair Display","DM Serif Display","Fraunces","Libre Baskerville","Merriweather","Lora",
"Cormorant Garamond","EB Garamond","Noto Serif","PT Serif","Source Serif 4","Crimson Pro","Spectral","Bitter",
"Roboto Slab","Zilla Slab","Arvo","Inter","Source Sans 3","Open Sans","Roboto","Lato","Montserrat","Poppins",
"Raleway","Nunito","Work Sans","DM Sans","Manrope","Outfit","Jost","Archivo","Space Grotesk","Sora","Lexend",
"Plus Jakarta Sans","Public Sans","Barlow","Fira Sans","Karla","Mulish","Heebo","Rubik","Cabin","PT Sans",
"Noto Sans","Exo 2","Titillium Web","Ubuntu","Varela Round","Oswald","Bebas Neue","Anton","Roboto Condensed",
"Barlow Condensed","Archivo Black","Josefin Sans","Quicksand","JetBrains Mono","Fira Code","Source Code Pro",
"IBM Plex Mono","Space Mono"]

LAYOUTS = ["classic","sidebar-left","sidebar-right","banner","timeline","editorial","cards","swiss","creative","compact"]
SAMPLES = ["engineer","designer","executive","general"]
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

def err(msg): print("ERROR:", msg)

def validate(cfg, seen):
    ok = True
    def bad(m):
        nonlocal ok; ok = False; err(f"[{cfg.get('slug','?')}] {m}")
    for k in ["slug","name","persona","sample","tags","layout","page","sidebar","fonts","header",
              "section_title","skills","experience","sections","accents","density"]:
        if k not in cfg: bad(f"missing key {k}")
    if not re.match(r"^[a-z0-9-]+$", cfg.get("slug","")): bad("slug must be kebab-case")
    if cfg.get("slug") in seen: bad("duplicate slug")
    seen.add(cfg.get("slug"))
    if cfg.get("sample") not in SAMPLES: bad("bad sample")
    if cfg.get("layout") not in LAYOUTS: bad("bad layout")
    if not (3 <= len(cfg.get("tags",[])) <= 5): bad("tags must be 3-5")
    for grp in ["page","sidebar"]:
        for ck in (["bg","ink","muted","accent","accent2","rule"] if grp=="page" else ["bg","ink","muted","accent"]):
            v = cfg.get(grp,{}).get(ck,"")
            if not HEX.match(v or ""): bad(f"{grp}.{ck} bad hex: {v}")
    for fk in ["display","body"]:
        if cfg.get("fonts",{}).get(fk) not in FONTS: bad(f"fonts.{fk} not in allowlist: {cfg.get('fonts',{}).get(fk)}")
    h = cfg.get("header",{})
    if h.get("align") not in ["left","center","right"]: bad("header.align")
    if h.get("photo") not in ["none","circle","rounded","square"]: bad("header.photo")
    if h.get("title_rule") not in ["none","accent-bar","full-rule"]: bad("header.title_rule")
    st = cfg.get("section_title",{})
    if st.get("style") not in ["rule","boxed","band","numbered","plain","sideline"]: bad("section_title.style")
    if st.get("case") not in ["upper","title"]: bad("section_title.case")
    if cfg.get("skills",{}).get("style") not in ["bars","chips","dots","columns","levels","list"]: bad("skills.style")
    if cfg.get("experience",{}).get("style") not in ["standard","timeline","card"]: bad("experience.style")
    if cfg.get("layout")=="timeline" and cfg.get("experience",{}).get("style")!="timeline":
        bad("timeline layout must use timeline experience style")
    order = cfg.get("sections",{}).get("order",[])
    if not order or order[0]!="summary": bad("sections.order must start with summary")
    for req in ["experience","skills","education"]:
        if req not in order: bad(f"sections.order missing {req}")
    if len(order) > 7: bad("sections.order max 7")
    if cfg.get("accents",{}).get("page_shape") not in ["none","diagonal","wave","arch","corners","dots"]: bad("accents.page_shape")
    if cfg.get("accents",{}).get("marker") not in ["dash","square","dot","chevron","none"]: bad("accents.marker")
    if cfg.get("density") not in ["comfortable","compact"]: bad("density")
    # contrast
    from renderer import contrast
    if contrast(cfg["page"]["ink"], cfg["page"]["bg"]) < 3.0: bad("page ink/bg contrast < 3.0")
    if cfg["layout"] in ("sidebar-left","sidebar-right"):
        if contrast(cfg["sidebar"]["ink"], cfg["sidebar"]["bg"]) < 3.0: bad("sidebar ink/bg contrast < 3.0")
    return ok

def main(path):
    data = json.load(open(path))
    items = data if isinstance(data, list) else [data]
    seen, ok = set(), True
    for cfg in items:
        ok = validate(cfg, seen) and ok
    print(f"{path}: {len(items)} configs, {'VALID' if ok else 'INVALID'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
