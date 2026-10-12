"""ResumeForge template renderer — part 1: helpers, skills, titles, headers, sections."""
import html

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)

def font_href(fonts):
    fams = []
    for f in (fonts.get("display"), fonts.get("body")):
        if f and f not in [x.split(":")[0] for x in fams]:
            fams.append(f.replace(" ", "+") + ":wght@400;500;600;700;800")
    return "https://fonts.googleapis.com/css2?family=" + "&family=".join(fams) + "&display=swap"

def initials(name):
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts[:2]).upper()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def luminance(h):
    r, g, b = [c / 255 for c in hex_to_rgb(h)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

ICONS = {
    "mail": '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "web": '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>',
}

MARKERS = {
    "dash": ("—",), "square": ("■",), "dot": ("●",), "chevron": ("›",), "none": ("",),
}

# ---------------------------------------------------------------- base CSS
def base_css(cfg, P):
    dense = cfg.get("density") == "compact"
    fs = "12px" if dense else "13.5px"
    lh = "1.5" if dense else "1.6"
    gap = "16px" if dense else "24px"
    pad = "34px" if dense else "46px"
    df, bf = cfg["fonts"]["display"], cfg["fonts"]["body"]
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#dfe3e8;display:flex;justify-content:center;padding:28px 12px;font-family:'{bf}',sans-serif}}
.page{{width:794px;min-height:1123px;background:{P['bg']};color:{P['ink']};position:relative;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.18);font-size:{fs};line-height:{lh}}}
@media print{{body{{padding:0;background:#fff;display:block}}.page{{box-shadow:none;margin:0}}}}
@page{{size:A4;margin:0}}
.pad{{padding:{pad}}}
.sec{{margin-bottom:{gap}}}
p{{margin:0}}
"""

# ---------------------------------------------------------------- section titles
def section_title(cfg, text, idx=0):
    st = cfg["section_title"]
    t = esc(text.upper()) if st["case"] == "upper" else esc(text)
    df = cfg["fonts"]["display"]
    size, tr = st["size"], st["tracking"]
    style = st["style"]
    if style == "rule":
        return (f'<div class="st-rule"><span style="font-size:{size}px;letter-spacing:{tr};'
                f'font-weight:700">{t}</span></div>')
    if style == "boxed":
        return (f'<div class="st-boxed"><span style="font-size:{size}px;letter-spacing:{tr};'
                f'font-weight:700">{t}</span></div>')
    if style == "band":
        return (f'<div class="st-band"><span style="font-size:{size}px;letter-spacing:{tr};'
                f'font-weight:700">{t}</span></div>')
    if style == "numbered":
        return (f'<div class="st-numbered"><span class="st-num" style="font-family:\'{df}\',serif">'
                f'{idx+1:02d}</span><span style="font-size:{size}px;letter-spacing:{tr};font-weight:700">{t}</span></div>')
    if style == "plain":
        return (f'<div class="st-plain" style="font-family:\'{df}\',serif">{t}</div>')
    # sideline
    return (f'<div class="st-sideline"><span style="font-size:{size}px;letter-spacing:{tr};'
            f'font-weight:700">{t}</span></div>')

def section_title_css(cfg, P):
    st = cfg["section_title"]
    df = cfg["fonts"]["display"]
    return f"""
.st-rule{{margin-bottom:10px}}.st-rule span{{color:{P['ink']}}}
.st-rule::after{{content:"";display:block;height:2px;background:{P['rule']};margin-top:6px;position:relative}}
.st-rule::before{{content:"";display:block;width:56px;height:2px;background:{P['accent']};margin-bottom:-2px;position:relative;top:8px;z-index:1}}
.st-boxed{{margin-bottom:12px}}.st-boxed span{{display:inline-block;border:1.5px solid {P['accent']};color:{P['accent']};padding:4px 12px;border-radius:3px}}
.st-band{{margin:0 -46px 12px;padding:8px 46px;background:{P['accent']};color:#fff}}
.st-numbered{{display:flex;align-items:baseline;gap:12px;margin-bottom:10px}}
.st-num{{font-size:26px;font-weight:800;color:{P['accent']};opacity:.9}}
.st-plain{{font-size:24px;font-weight:700;margin-bottom:10px;color:{P['ink']}}}
.st-sideline{{border-left:5px solid {P['accent']};padding-left:12px;margin-bottom:10px}}
"""

# ---------------------------------------------------------------- skills
def skills_html(cfg, skills, P, dark=False):
    style = cfg["skills"]["style"]
    ink = P.get("ink", "#111"); acc = P.get("accent", "#0B5FFF"); mut = P.get("muted", "#888")
    if style == "bars":
        rows = "".join(
            f'<div class="sk-bar"><div class="sk-bar-top"><span>{esc(s["name"])}</span></div>'
            f'<div class="sk-track"><div class="sk-fill" style="width:{s["level"]}%"></div></div></div>'
            for s in skills)
        return f'<div class="sk-bars">{rows}</div>'
    if style == "chips":
        chips = "".join(f'<span class="sk-chip">{esc(s["name"])}</span>' for s in skills)
        return f'<div class="sk-chips">{chips}</div>'
    if style == "dots":
        rows = "".join(
            f'<div class="sk-dot-row"><span class="sk-dot-name">{esc(s["name"])}</span><span class="sk-dots">'
            + "".join(f'<i class="{"on" if i < round(s["level"]/20) else ""}"></i>' for i in range(5))
            + '</span></div>' for s in skills)
        return f'<div class="sk-dots-wrap">{rows}</div>'
    if style == "columns":
        items = "".join(f'<li>{esc(s["name"])}</li>' for s in skills)
        return f'<ul class="sk-cols">{items}</ul>'
    if style == "levels":
        rows = "".join(
            f'<div class="sk-lvl"><span>{esc(s["name"])}</span><div class="sk-lvl-track">'
            f'<div class="sk-lvl-fill" style="width:{s["level"]}%"></div></div></div>'
            for s in skills)
        return f'<div class="sk-lvls">{rows}</div>'
    # list
    return f'<p class="sk-list">{" &nbsp;·&nbsp; ".join(esc(s["name"]) for s in skills)}</p>'

def skills_css(cfg, P):
    acc, rule, mut = P["accent"], P["rule"], P["muted"]
    return f"""
.sk-bars{{display:grid;gap:9px}}.sk-bar-top{{font-size:12px;font-weight:600;margin-bottom:3px}}
.sk-track{{height:6px;background:{rule};border-radius:3px;overflow:hidden}}
.sk-fill{{height:100%;background:{acc};border-radius:3px}}
.sk-chips{{display:flex;flex-wrap:wrap;gap:7px}}
.sk-chip{{border:1px solid {acc};color:{acc};border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600}}
.sk-dot-row{{display:flex;justify-content:space-between;align-items:center;padding:4px 0}}
.sk-dot-name{{font-size:12.5px}}.sk-dots{{display:flex;gap:4px}}.sk-dots i{{width:9px;height:9px;border-radius:50%;background:{rule};display:block}}
.sk-dots i.on{{background:{acc}}}
.sk-cols{{list-style:none;columns:2;column-gap:18px;font-size:12.5px}}.sk-cols li{{padding:3px 0;break-inside:avoid}}
.sk-cols li::before{{content:"▸";color:{acc};margin-right:6px}}
.sk-lvls{{display:grid;gap:8px}}.sk-lvl{{display:grid;grid-template-columns:1fr 110px;gap:10px;align-items:center;font-size:12.5px}}
.sk-lvl-track{{height:4px;background:{rule};border-radius:2px}}.sk-lvl-fill{{height:100%;background:{acc};border-radius:2px}}
.sk-list{{font-size:13px;color:{mut};line-height:1.9}}
"""

# ---------------------------------------------------------------- header
def photo_html(cfg, d, P):
    ph = cfg["header"]["photo"]
    if ph == "none":
        return ""
    rad = {"circle": "50%", "rounded": "18%", "square": "6px"}[ph]
    ini = initials(d["name"])
    return (f'<div class="photo" style="border-radius:{rad};background:{P["accent"]};color:#fff">'
            f'{esc(ini)}</div>')

def contact_row(d, color=None):
    items = [
        (ICONS["mail"], d["email"]), (ICONS["phone"], d["phone"]),
        (ICONS["pin"], d["location"]), (ICONS["web"], d["website"]),
        (ICONS["link"], d["linkedin"]),
    ]
    style = f' style="color:{color}"' if color else ""
    return ("<div class=\"contact\"" + style + ">" + "".join(
        f'<span class="c-item"><span class="c-ic">{ic}</span>{esc(v)}</span>'
        for ic, v in items) + "</div>")

def header_html(cfg, d, P):
    h = cfg["header"]
    df = cfg["fonts"]["display"]
    photo = photo_html(cfg, d, P)
    rule_html = ""
    if h["title_rule"] == "accent-bar":
        rule_html = f'<div class="h-bar" style="background:{P["accent"]}"></div>'
    elif h["title_rule"] == "full-rule":
        rule_html = f'<div class="h-rule" style="background:{P["rule"]}"></div>'
    inner = (f'<div class="h-name" style="font-family:\'{df}\',serif;font-size:{h["name_size"]}px">{esc(d["name"])}</div>'
             f'<div class="h-title">{esc(d["title"])}</div>{rule_html}{contact_row(d)}')
    if photo and h["align"] in ("left", "right"):
        return (f'<header class="hdr hdr-{h["align"]}"><div class="h-text">{inner}</div>{photo}</header>'
                if h["align"] == "left" else
                f'<header class="hdr hdr-{h["align"]}">{photo}<div class="h-text">{inner}</div></header>')
    return f'<header class="hdr hdr-{h["align"]}">{photo}<div class="h-text">{inner}</div></header>'

def header_css(cfg, P):
    return f"""
.hdr{{display:flex;gap:22px;align-items:center;margin-bottom:22px}}
.hdr-center{{flex-direction:column;text-align:center}}
.hdr-right .h-text{{text-align:right}}.hdr-right{{justify-content:flex-end}}
.photo{{width:96px;height:96px;flex:none;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:800;letter-spacing:.05em}}
.hdr-center .photo{{margin:0 auto}}
.h-name{{font-weight:800;line-height:1.15;letter-spacing:.01em}}
.h-title{{font-size:15px;color:{P['accent']};font-weight:600;margin-top:4px;letter-spacing:.06em}}
.h-bar{{width:64px;height:4px;margin:10px 0 12px;border-radius:2px}}
.hdr-center .h-bar{{margin-left:auto;margin-right:auto}}
.h-rule{{height:1px;margin:10px 0 12px}}
.contact{{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:8px;font-size:11.5px;color:{P['muted']}}}
.hdr-center .contact{{justify-content:center}}.hdr-right .contact{{justify-content:flex-end}}
.c-item{{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}}
.c-ic{{display:inline-flex;color:{P['accent']}}}
"""

# ---------------------------------------------------------------- experience / sections
def bullets_html(items, cfg, P):
    mk = MARKERS[cfg["accents"]["marker"]][0]
    if cfg["accents"]["marker"] == "none":
        lis = "".join(f"<li>{esc(b)}</li>" for b in items)
        return f'<ul class="bullets plain">{lis}</ul>'
    lis = "".join(f'<li data-mk="{esc(mk)}">{esc(b)}</li>' for b in items)
    return f'<ul class="bullets custom" style="--mkc:{P["accent"]}">{lis}</ul>'

def bullets_css():
    return """
.bullets{list-style:none;margin-top:6px;display:grid;gap:5px;font-size:12.8px}
.bullets.plain{list-style:disc;padding-left:18px}
.bullets.custom li{padding-left:20px;position:relative}
.bullets.custom li::before{content:attr(data-mk);position:absolute;left:0;color:var(--mkc);font-weight:700}
"""

def experience_html(cfg, d, P):
    style = cfg["experience"]["style"]
    jobs = d["experience"]
    if style == "timeline":
        items = "".join(
            f'<div class="tl-item"><div class="tl-dot" style="border-color:{P["accent"]}"></div>'
            f'<div class="tl-body"><div class="tl-head"><span class="tl-role">{esc(j["role"])}</span>'
            f'<span class="tl-period">{esc(j["period"])}</span></div>'
            f'<div class="tl-co" style="color:{P["accent"]}">{esc(j["company"])} · {esc(j["location"])}</div>'
            f'{bullets_html(j["bullets"], cfg, P)}</div></div>'
            for j in jobs)
        return f'<div class="tl" style="--tlc:{P["rule"]}">{items}</div>'
    if style == "card":
        items = "".join(
            f'<div class="job-card" style="border-color:{P["rule"]}">'
            f'<div class="jc-head"><span class="jc-role">{esc(j["role"])}</span>'
            f'<span class="jc-period">{esc(j["period"])}</span></div>'
            f'<div class="jc-co" style="color:{P["accent"]}">{esc(j["company"])} · {esc(j["location"])}</div>'
            f'{bullets_html(j["bullets"], cfg, P)}</div>'
            for j in jobs)
        return f'<div class="job-cards">{items}</div>'
    items = "".join(
        f'<div class="job"><div class="job-head"><span class="job-role">{esc(j["role"])}</span>'
        f'<span class="job-period">{esc(j["period"])}</span></div>'
        f'<div class="job-co" style="color:{P["accent"]}">{esc(j["company"])} · {esc(j["location"])}</div>'
        f'{bullets_html(j["bullets"], cfg, P)}</div>'
        for j in jobs)
    return f'<div class="jobs">{items}</div>'

def experience_css(P):
    return f"""
.jobs{{display:grid;gap:14px}}.job-head,.jc-head,.tl-head{{display:flex;justify-content:space-between;align-items:baseline;gap:12px}}
.job-role,.jc-role,.tl-role{{font-weight:700;font-size:14px}}
.job-period,.jc-period,.tl-period{{font-size:11.5px;color:{P['muted']};white-space:nowrap;font-weight:600}}
.job-co,.jc-co,.tl-co{{font-size:12.5px;font-weight:600;margin:2px 0 2px}}
.job-cards{{display:grid;gap:12px}}.job-card{{border:1px solid;border-radius:8px;padding:14px 16px}}
.tl{{position:relative;padding-left:26px}}.tl::before{{content:"";position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:var(--tlc)}}
.tl-item{{position:relative;margin-bottom:16px}}.tl-item:last-child{{margin-bottom:0}}
.tl-dot{{position:absolute;left:-26px;top:5px;width:16px;height:16px;border-radius:50%;background:#fff;border:3px solid}}
"""

def education_html(d):
    return "".join(
        f'<div class="edu"><div class="edu-head"><span class="edu-deg">{esc(e["degree"])}</span>'
        f'<span class="edu-period">{esc(e["period"])}</span></div>'
        f'<div class="edu-school">{esc(e["school"])}</div>'
        + (f'<div class="edu-detail">{esc(e["detail"])}</div>' if e.get("detail") else "")
        + '</div>' for e in d["education"])

def section_block(cfg, key, d, P, idx):
    titles = {"summary": "Profile", "experience": "Experience", "skills": "Skills",
              "education": "Education", "projects": "Projects",
              "certifications": "Certifications", "languages": "Languages"}
    t = section_title(cfg, titles[key], idx)
    if key == "summary":
        body = f'<p class="summary">{esc(d["summary"])}</p>'
    elif key == "experience":
        body = experience_html(cfg, d, P)
    elif key == "skills":
        body = skills_html(cfg, d["skills"], P)
    elif key == "education":
        body = f'<div class="edus">{education_html(d)}</div>'
    elif key == "projects":
        body = "".join(f'<div class="proj"><span class="proj-name">{esc(p["name"])}</span>'
                       f'<span class="proj-sep"> — </span><span class="proj-det">{esc(p["detail"])}</span></div>'
                       for p in d["projects"])
        body = f'<div class="projs">{body}</div>'
    elif key == "certifications":
        body = "<ul class='certs'>" + "".join(f"<li>{esc(c)}</li>" for c in d["certifications"]) + "</ul>"
    else:
        body = "<p class='langs'>" + " &nbsp;·&nbsp; ".join(esc(l) for l in d["languages"]) + "</p>"
    return f'<section class="sec">{t}{body}</section>'

def sections_css(P):
    return f"""
.summary{{font-size:13.2px}}
.edus{{display:grid;gap:10px}}.edu-head{{display:flex;justify-content:space-between;gap:12px}}
.edu-deg{{font-weight:700;font-size:13.5px}}.edu-period{{font-size:11.5px;color:{P['muted']};font-weight:600;white-space:nowrap}}
.edu-school{{font-size:12.5px;color:{P['accent']};font-weight:600}}.edu-detail{{font-size:12px;color:{P['muted']}}}
.projs{{display:grid;gap:8px;font-size:12.8px}}.proj-name{{font-weight:700}}
.certs{{list-style:none;display:grid;gap:5px;font-size:12.8px}}.certs li::before{{content:"✓ ";color:{P['accent']};font-weight:700}}
.langs{{font-size:12.8px}}
"""

# ---------------------------------------------------------------- page shapes
def page_shape_html(cfg, P):
    s = cfg["accents"]["page_shape"]
    if s == "diagonal":
        return (f'<div class="shape" style="position:absolute;top:0;right:0;width:220px;height:220px;'
                f'background:{P["accent"]};clip-path:polygon(100% 0,0 0,100% 100%);opacity:.14"></div>')
    if s == "wave":
        return (f'<svg class="shape" style="position:absolute;top:0;left:0;width:100%;height:90px" '
                f'viewBox="0 0 794 90" preserveAspectRatio="none"><path d="M0 0h794v38c-120 30-260 30-397 0S120 50 0 62z" '
                f'fill="{P["accent"]}" opacity=".16"/></svg>')
    if s == "arch":
        return (f'<div class="shape" style="position:absolute;top:-70px;left:50%;transform:translateX(-50%);'
                f'width:560px;height:280px;background:{P["accent"]};opacity:.12;border-radius:0 0 280px 280px"></div>')
    if s == "corners":
        c = P["accent"]
        return ("<div class='shape corners'>"
                f"<i style='top:14px;left:14px;border-top:5px solid {c};border-left:5px solid {c}'></i>"
                f"<i style='top:14px;right:14px;border-top:5px solid {c};border-right:5px solid {c}'></i>"
                f"<i style='bottom:14px;left:14px;border-bottom:5px solid {c};border-left:5px solid {c}'></i>"
                f"<i style='bottom:14px;right:14px;border-bottom:5px solid {c};border-right:5px solid {c}'></i></div>"
                "<style>.corners i{position:absolute;width:56px;height:56px}</style>")
    if s == "dots":
        return (f'<div class="shape" style="position:absolute;top:0;right:0;width:260px;height:180px;opacity:.5;'
                f'background-image:radial-gradient({P["accent"]} 1.6px,transparent 1.6px);'
                f'background-size:18px 18px;mask-image:linear-gradient(to bottom left,#000,transparent)}}"></div>')
    return ""

# ---------------------------------------------------------------- layouts
def layout_classic(cfg, d, P):
    secs = "".join(section_block(cfg, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return (f'<div class="page">{page_shape_html(cfg, P)}<div class="pad">'
            f'{header_html(cfg, d, P)}{secs}</div></div>')

def layout_sidebar(cfg, d, P, side):
    S = cfg["sidebar"]
    order = [k for k in cfg["sections"]["order"] if k not in ("skills",)]
    main_secs = "".join(section_block(cfg, k, d, P, i) for i, k in enumerate(order))
    contact_items = [
        (ICONS["mail"], d["email"]), (ICONS["phone"], d["phone"]),
        (ICONS["pin"], d["location"]), (ICONS["web"], d["website"]),
        (ICONS["link"], d["linkedin"])]
    side_contact = "".join(
        f'<div class="s-c"><span class="s-ic">{ic}</span><span>{esc(v)}</span></div>'
        for ic, v in contact_items)
    df = cfg["fonts"]["display"]
    photo = photo_html(cfg, d, P)
    aside = (
        f'<aside class="sb" style="background:' + S['bg'] + ';color:' + S['ink'] + '">'
        f'{photo}'
        f'<div class="s-sec"><div class="s-h" style="color:{S["accent"]}">Contact</div>{side_contact}</div>'
        f'<div class="s-sec"><div class="s-h" style="color:{S["accent"]}">Skills</div>'
        f'{skills_html(cfg, d["skills"], {"ink": S["ink"], "accent": S["accent"], "muted": S["muted"], "rule": "rgba(128,128,128,.35)"})}</div>'
        f'<div class="s-sec"><div class="s-h" style="color:{S["accent"]}">Languages</div>'
        f'<div class="s-list">{"<br>".join(esc(l) for l in d["languages"])}</div></div>'
        f'<div class="s-sec"><div class="s-h" style="color:{S["accent"]}">Certifications</div>'
        f'<div class="s-list">{"<br>".join(esc(c) for c in d["certifications"])}</div></div>'
        f'</aside>')
    head = (f'<div class="sb-head"><div class="sb-name" style="font-family:\'{df}\',serif">{esc(d["name"])}</div>'
            f'<div class="sb-title" style="color:{P["accent"]}">{esc(d["title"])}</div></div>')
    main = f'<main class="sb-main"><div class="pad">{head}{main_secs}</div></main>'
    inner = aside + main if side == "left" else main + aside
    return f'<div class="page"><div class="sb-wrap">{inner}</div></div>'

def sidebar_css(P):
    return """
.sb-wrap{display:flex;min-height:1123px}
.sb{width:262px;flex:none;padding:38px 26px}
.sb .photo{margin-bottom:20px;width:120px;height:120px}
.sb-main{flex:1}
.s-sec{margin-bottom:22px}.s-h{font-size:11px;font-weight:800;letter-spacing:.22em;text-transform:uppercase;margin-bottom:10px}
.s-c{display:flex;gap:8px;align-items:flex-start;font-size:11.5px;margin-bottom:8px;line-height:1.45}
.s-ic{flex:none;margin-top:2px}
.s-list{font-size:11.5px;line-height:1.7}
.sb .sk-chip{border-color:currentColor;color:inherit}
.sb .sk-track,.sb .sk-lvl-track{background:rgba(128,128,128,.35)}
.sb-name{font-size:32px;font-weight:800;line-height:1.15;margin-bottom:4px}
.sb-title{font-size:14px;font-weight:600;letter-spacing:.08em;margin-bottom:20px}
"""

def layout_banner(cfg, d, P):
    df = cfg["fonts"]["display"]
    photo = photo_html(cfg, d, P)
    banner = (
        f'<div class="bnr" style="background:{P["accent"]};color:#fff">'
        f'{photo}<div><div class="bnr-name" style="font-family:\'{df}\',serif">{esc(d["name"])}</div>'
        f'<div class="bnr-title">{esc(d["title"])}</div>{contact_row(d, color="#fff")}</div></div>')
    secs = "".join(section_block(cfg, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return (f'<div class="page">{banner}<div class="pad">{secs}</div></div>')

def banner_css():
    return """
.bnr{display:flex;gap:24px;align-items:center;padding:40px 46px}
.bnr .photo{background:rgba(255,255,255,.22)!important}
.bnr-name{font-size:38px;font-weight:800;line-height:1.1}
.bnr-title{font-size:15px;font-weight:600;letter-spacing:.1em;margin-top:6px;opacity:.92}
.bnr .contact{color:#fff}.bnr .c-ic{color:#fff}
"""

def layout_timeline(cfg, d, P):
    cfg2 = dict(cfg); cfg2["experience"] = {"style": "timeline"}
    secs = "".join(section_block(cfg2, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return (f'<div class="page">{page_shape_html(cfg, P)}<div class="pad">'
            f'{header_html(cfg, d, P)}{secs}</div></div>')

def layout_editorial(cfg, d, P):
    df = cfg["fonts"]["display"]
    photo = photo_html(cfg, d, P)
    head = (f'<header class="ed-head">{photo}<div class="ed-name" style="font-family:\'{df}\',serif">'
            f'{esc(d["name"])}</div><div class="ed-title" style="color:{P["accent"]}">'
            f'{esc(d["title"])} &nbsp;·&nbsp; {esc(d["location"])}</div>'
            f'<div class="ed-rule" style="background:{P["accent"]}"></div>'
            f'{contact_row(d)}</header>')
    secs = "".join(section_block(cfg, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return f'<div class="page"><div class="pad ed">{head}{secs}</div></div>'

def editorial_css(P):
    return f"""
.ed-head{{margin-bottom:24px}}.ed-head .photo{{margin-bottom:14px}}
.ed-name{{font-size:44px;font-weight:700;line-height:1.05;letter-spacing:-.01em}}
.ed-title{{font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;margin:8px 0 12px}}
.ed-rule{{width:72px;height:5px;margin-bottom:12px}}
.ed .sec p.summary{{font-size:14.5px;line-height:1.75}}
.ed .jobs{{columns:2;column-gap:28px}}.ed .job{{break-inside:avoid;margin-bottom:16px}}
"""

def layout_cards(cfg, d, P):
    cfg2 = dict(cfg); cfg2["experience"] = {"style": "card"}
    secs = "".join(section_block(cfg2, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return (f'<div class="page">{page_shape_html(cfg, P)}<div class="pad">'
            f'{header_html(cfg, d, P)}{secs}</div></div>')

def layout_swiss(cfg, d, P):
    items = [
        ("Name", d["name"]), ("Title", d["title"]), ("Mail", d["email"]),
        ("Phone", d["phone"]), ("Place", d["location"]), ("Web", d["website"])]
    grid = "".join(
        f'<div class="sw-cell"><div class="sw-k">{k}</div><div class="sw-v">{esc(v)}</div></div>'
        for k, v in items)
    secs = "".join(section_block(cfg, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return (f'<div class="page"><div class="pad"><div class="sw-grid" '
            f'style="border-color:{P["rule"]}">{grid}</div>'
            f'<div class="sw-rule" style="background:{P["ink"]}"></div>{secs}</div></div>')

def swiss_css(P):
    return f"""
.sw-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;border-top:1px solid;border-bottom:1px solid;margin-bottom:6px}}
.sw-cell{{padding:10px 12px;border-right:1px solid {P['rule']}}}
.sw-cell:nth-child(3n){{border-right:none}}
.sw-k{{font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:{P['muted']};font-weight:700}}
.sw-v{{font-size:13px;font-weight:600;margin-top:2px}}
.sw-rule{{height:3px;margin:14px 0 22px}}
"""

def layout_creative(cfg, d, P):
    df = cfg["fonts"]["display"]
    photo = photo_html(cfg, d, P)
    head = (f'<header class="cr-head"><div class="cr-geo" style="background:{P["accent2"]}"></div>'
            f'<div><div class="cr-kicker" style="color:{P["accent"]}">Résumé — {esc(d["title"])}</div>'
            f'<div class="cr-name" style="font-family:\'{df}\',serif">{esc(d["name"])}</div></div>'
            f'{photo}</header>')
    secs = "".join(section_block(cfg, k, d, P, i)
                   for i, k in enumerate(cfg["sections"]["order"]))
    return f'<div class="page"><div class="pad">{head}{secs}</div></div>'

def creative_css(P):
    return f"""
.cr-head{{display:flex;align-items:center;gap:20px;margin-bottom:26px;position:relative}}
.cr-geo{{position:absolute;left:-46px;top:-10px;width:14px;height:120px;transform:skewX(-12deg)}}
.cr-kicker{{font-size:11px;font-weight:800;letter-spacing:.26em;text-transform:uppercase;margin-bottom:8px}}
.cr-name{{font-size:52px;font-weight:800;line-height:1;letter-spacing:-.015em}}
.cr-head .photo{{margin-left:auto}}
"""

def layout_compact(cfg, d, P):
    df = cfg["fonts"]["display"]
    head = (f'<header class="cp-head"><div><div class="cp-name" style="font-family:\'{df}\',serif">'
            f'{esc(d["name"])}</div><div class="cp-title" style="color:{P["accent"]}">'
            f'{esc(d["title"])}</div></div>'
            f'<div class="cp-contact">{esc(d["email"])} · {esc(d["phone"])}<br>'
            f'{esc(d["location"])} · {esc(d["website"])}</div></header>')
    main_keys = [k for k in cfg["sections"]["order"] if k in ("summary", "experience", "projects")]
    side_keys = [k for k in cfg["sections"]["order"] if k in ("skills", "education", "certifications", "languages")]
    main = "".join(section_block(cfg, k, d, P, i) for i, k in enumerate(main_keys))
    side = "".join(section_block(cfg, k, d, P, i) for i, k in enumerate(side_keys))
    return (f'<div class="page"><div class="pad"><div class="cp-wrap">'
            f'<div class="cp-main">{head}{main}</div>'
            f'<div class="cp-side" style="border-color:{P["rule"]}">{side}</div>'
            f'</div></div></div>')

def compact_css(P):
    return f"""
.cp-wrap{{display:grid;grid-template-columns:1.9fr 1fr;gap:26px}}
.cp-side{{border-left:1px solid;padding-left:20px}}
.cp-head{{margin-bottom:16px}}
.cp-name{{font-size:26px;font-weight:800}}
.cp-title{{font-size:13px;font-weight:700;letter-spacing:.06em;margin-top:2px}}
.cp-contact{{font-size:10.5px;color:{P['muted']};margin-top:8px;line-height:1.7}}
"""

LAYOUTS = {
    "classic": layout_classic, "sidebar-left": lambda c, d, p: layout_sidebar(c, d, p, "left"),
    "sidebar-right": lambda c, d, p: layout_sidebar(c, d, p, "right"),
    "banner": layout_banner, "timeline": layout_timeline, "editorial": layout_editorial,
    "cards": layout_cards, "swiss": layout_swiss, "creative": layout_creative,
    "compact": layout_compact,
}

# ---------------------------------------------------------------- render entry
def render(cfg, data):
    P = cfg["page"]
    df, bf = cfg["fonts"]["display"], cfg["fonts"]["body"]
    css = (base_css(cfg, P) + section_title_css(cfg, P) + skills_css(cfg, P)
           + header_css(cfg, P) + bullets_css() + experience_css(P) + sections_css(P)
           + sidebar_css(P) + banner_css() + editorial_css(P) + swiss_css(P)
           + creative_css(P) + compact_css(P))
    body = LAYOUTS[cfg["layout"]](cfg, data, P)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(cfg['name'])} — Resume Template</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font_href(cfg['fonts'])}" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""

if __name__ == "__main__":
    import json, sys
    from sample_data import SAMPLES
    cfg = json.load(open(sys.argv[1]))
    data = SAMPLES[cfg.get("sample", "engineer")]
    sys.stdout.write(render(cfg, data))
