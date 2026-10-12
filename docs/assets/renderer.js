/* ResumeForge renderer.js — faithful JS port of engine/renderer.py
 * renderTemplate(cfg, data) -> standalone A4 HTML string.
 * Works in browser (window.RF_RENDER) and node (module.exports). */
"use strict";

function rfEsc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}

function rfFontHref(fonts) {
  const seen = [];
  const fams = [];
  for (const f of [fonts.display, fonts.body]) {
    if (f && !seen.includes(f)) { seen.push(f); fams.push(f.replace(/ /g, "+") + ":wght@400;500;600;700;800"); }
  }
  return "https://fonts.googleapis.com/css2?family=" + fams.join("&family=") + "&display=swap";
}

function rfInitials(name) {
  const parts = String(name).split(/\s+/).filter(Boolean);
  return (parts.slice(0, 2).map(p => p[0]).join("")).toUpperCase();
}

/* Python round() is banker's rounding — mirror it for skill dots. */
function rfPyRound(x) {
  const f = Math.floor(x), d = x - f;
  if (d < 0.5) return f;
  if (d > 0.5) return f + 1;
  return (f % 2 === 0) ? f : f + 1;
}

const RF_ICONS = {
  mail: '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/></svg>',
  phone: '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/></svg>',
  pin: '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  web: '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
  link: '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>'
};

const RF_MARKERS = { dash: "—", square: "■", dot: "●", chevron: "›", none: "" };

function rfBaseCss(cfg, P) {
  const dense = cfg.density === "compact";
  const fs = dense ? "12px" : "13.5px", lh = dense ? "1.5" : "1.6";
  const gap = dense ? "16px" : "24px", pad = dense ? "34px" : "46px";
  const bf = cfg.fonts.body;
  return `
*{box-sizing:border-box;margin:0;padding:0}
body{background:#dfe3e8;display:flex;justify-content:center;padding:28px 12px;font-family:'${bf}',sans-serif}
.page{width:794px;min-height:1123px;background:${P.bg};color:${P.ink};position:relative;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.18);font-size:${fs};line-height:${lh}}
@media print{body{padding:0;background:#fff;display:block}.page{box-shadow:none;margin:0}}
@page{size:A4;margin:0}
.pad{padding:${pad}}
.sec{margin-bottom:${gap}}
p{margin:0}
`;
}

function rfSectionTitle(cfg, text, idx) {
  idx = idx || 0;
  const st = cfg.section_title;
  const t = rfEsc(st.case === "upper" ? text.toUpperCase() : text);
  const df = cfg.fonts.display, size = st.size, tr = st.tracking;
  const inner = `<span style="font-size:${size}px;letter-spacing:${tr};font-weight:700">${t}</span>`;
  switch (st.style) {
    case "rule": return `<div class="st-rule">${inner}</div>`;
    case "boxed": return `<div class="st-boxed">${inner}</div>`;
    case "band": return `<div class="st-band">${inner}</div>`;
    case "numbered": return `<div class="st-numbered"><span class="st-num" style="font-family:'${df}',serif">${String(idx + 1).padStart(2, "0")}</span>${inner}</div>`;
    case "plain": return `<div class="st-plain" style="font-family:'${df}',serif">${t}</div>`;
    default: return `<div class="st-sideline">${inner}</div>`;
  }
}

function rfSectionTitleCss(cfg, P) {
  return `
.st-rule{margin-bottom:10px}.st-rule span{color:${P.ink}}
.st-rule::after{content:"";display:block;height:2px;background:${P.rule};margin-top:6px;position:relative}
.st-rule::before{content:"";display:block;width:56px;height:2px;background:${P.accent};margin-bottom:-2px;position:relative;top:8px;z-index:1}
.st-boxed{margin-bottom:12px}.st-boxed span{display:inline-block;border:1.5px solid ${P.accent};color:${P.accent};padding:4px 12px;border-radius:3px}
.st-band{margin:0 -46px 12px;padding:8px 46px;background:${P.accent};color:#fff}
.st-numbered{display:flex;align-items:baseline;gap:12px;margin-bottom:10px}
.st-num{font-size:26px;font-weight:800;color:${P.accent};opacity:.9}
.st-plain{font-size:24px;font-weight:700;margin-bottom:10px;color:${P.ink}}
.st-sideline{border-left:5px solid ${P.accent};padding-left:12px;margin-bottom:10px}
`;
}

function rfSkillsHtml(cfg, skills, P) {
  const style = cfg.skills.style;
  if (style === "bars") {
    const rows = skills.map(s =>
      `<div class="sk-bar"><div class="sk-bar-top"><span>${rfEsc(s.name)}</span></div>` +
      `<div class="sk-track"><div class="sk-fill" style="width:${s.level}%"></div></div></div>`).join("");
    return `<div class="sk-bars">${rows}</div>`;
  }
  if (style === "chips") {
    return `<div class="sk-chips">${skills.map(s => `<span class="sk-chip">${rfEsc(s.name)}</span>`).join("")}</div>`;
  }
  if (style === "dots") {
    const rows = skills.map(s => {
      const on = rfPyRound(s.level / 20);
      let dots = "";
      for (let i = 0; i < 5; i++) dots += `<i class="${i < on ? "on" : ""}"></i>`;
      return `<div class="sk-dot-row"><span class="sk-dot-name">${rfEsc(s.name)}</span><span class="sk-dots">${dots}</span></div>`;
    }).join("");
    return `<div class="sk-dots-wrap">${rows}</div>`;
  }
  if (style === "columns") {
    return `<ul class="sk-cols">${skills.map(s => `<li>${rfEsc(s.name)}</li>`).join("")}</ul>`;
  }
  if (style === "levels") {
    const rows = skills.map(s =>
      `<div class="sk-lvl"><span>${rfEsc(s.name)}</span><div class="sk-lvl-track">` +
      `<div class="sk-lvl-fill" style="width:${s.level}%"></div></div></div>`).join("");
    return `<div class="sk-lvls">${rows}</div>`;
  }
  return `<p class="sk-list">${skills.map(s => rfEsc(s.name)).join(" &nbsp;·&nbsp; ")}</p>`;
}

function rfSkillsCss(P) {
  const acc = P.accent, rule = P.rule, mut = P.muted;
  return `
.sk-bars{display:grid;gap:9px}.sk-bar-top{font-size:12px;font-weight:600;margin-bottom:3px}
.sk-track{height:6px;background:${rule};border-radius:3px;overflow:hidden}
.sk-fill{height:100%;background:${acc};border-radius:3px}
.sk-chips{display:flex;flex-wrap:wrap;gap:7px}
.sk-chip{border:1px solid ${acc};color:${acc};border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600}
.sk-dot-row{display:flex;justify-content:space-between;align-items:center;padding:4px 0}
.sk-dot-name{font-size:12.5px}.sk-dots{display:flex;gap:4px}.sk-dots i{width:9px;height:9px;border-radius:50%;background:${rule};display:block}
.sk-dots i.on{background:${acc}}
.sk-cols{list-style:none;columns:2;column-gap:18px;font-size:12.5px}.sk-cols li{padding:3px 0;break-inside:avoid}
.sk-cols li::before{content:"▸";color:${acc};margin-right:6px}
.sk-lvls{display:grid;gap:8px}.sk-lvl{display:grid;grid-template-columns:1fr 110px;gap:10px;align-items:center;font-size:12.5px}
.sk-lvl-track{height:4px;background:${rule};border-radius:2px}.sk-lvl-fill{height:100%;background:${acc};border-radius:2px}
.sk-list{font-size:13px;color:${mut};line-height:1.9}
`;
}

function rfPhotoHtml(cfg, d, P) {
  const ph = cfg.header.photo;
  if (ph === "none") return "";
  const rad = ph === "circle" ? "50%" : ph === "rounded" ? "18%" : "6px";
  return `<div class="photo" style="border-radius:${rad};background:${P.accent};color:#fff">${rfEsc(rfInitials(d.name))}</div>`;
}

function rfContactRow(d, color) {
  const items = [[RF_ICONS.mail, d.email], [RF_ICONS.phone, d.phone], [RF_ICONS.pin, d.location], [RF_ICONS.web, d.website], [RF_ICONS.link, d.linkedin]];
  const style = color ? ` style="color:${color}"` : "";
  return `<div class="contact"${style}>` + items.map(([ic, v]) =>
    `<span class="c-item"><span class="c-ic">${ic}</span>${rfEsc(v)}</span>`).join("") + `</div>`;
}

function rfHeaderHtml(cfg, d, P) {
  const h = cfg.header, df = cfg.fonts.display;
  const photo = rfPhotoHtml(cfg, d, P);
  let ruleHtml = "";
  if (h.title_rule === "accent-bar") ruleHtml = `<div class="h-bar" style="background:${P.accent}"></div>`;
  else if (h.title_rule === "full-rule") ruleHtml = `<div class="h-rule" style="background:${P.rule}"></div>`;
  const inner = `<div class="h-name" style="font-family:'${df}',serif;font-size:${h.name_size}px">${rfEsc(d.name)}</div>` +
    `<div class="h-title">${rfEsc(d.title)}</div>${ruleHtml}${rfContactRow(d)}`;
  if (photo && (h.align === "left" || h.align === "right")) {
    return h.align === "left"
      ? `<header class="hdr hdr-left"><div class="h-text">${inner}</div>${photo}</header>`
      : `<header class="hdr hdr-right">${photo}<div class="h-text">${inner}</div></header>`;
  }
  return `<header class="hdr hdr-${h.align}">${photo}<div class="h-text">${inner}</div></header>`;
}

function rfHeaderCss(P) {
  return `
.hdr{display:flex;gap:22px;align-items:center;margin-bottom:22px}
.hdr-center{flex-direction:column;text-align:center}
.hdr-right .h-text{text-align:right}.hdr-right{justify-content:flex-end}
.photo{width:96px;height:96px;flex:none;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:800;letter-spacing:.05em}
.hdr-center .photo{margin:0 auto}
.h-name{font-weight:800;line-height:1.15;letter-spacing:.01em}
.h-title{font-size:15px;color:${P.accent};font-weight:600;margin-top:4px;letter-spacing:.06em}
.h-bar{width:64px;height:4px;margin:10px 0 12px;border-radius:2px}
.hdr-center .h-bar{margin-left:auto;margin-right:auto}
.h-rule{height:1px;margin:10px 0 12px}
.contact{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:8px;font-size:11.5px;color:${P.muted}}
.hdr-center .contact{justify-content:center}.hdr-right .contact{justify-content:flex-end}
.c-item{display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
.c-ic{display:inline-flex;color:${P.accent}}
`;
}

function rfBulletsHtml(items, cfg, P) {
  const mk = RF_MARKERS[cfg.accents.marker];
  if (cfg.accents.marker === "none") {
    return `<ul class="bullets plain">${items.map(b => `<li>${rfEsc(b)}</li>`).join("")}</ul>`;
  }
  return `<ul class="bullets custom" style="--mkc:${P.accent}">` +
    items.map(b => `<li data-mk="${rfEsc(mk)}">${rfEsc(b)}</li>`).join("") + `</ul>`;
}

function rfBulletsCss() {
  return `
.bullets{list-style:none;margin-top:6px;display:grid;gap:5px;font-size:12.8px}
.bullets.plain{list-style:disc;padding-left:18px}
.bullets.custom li{padding-left:20px;position:relative}
.bullets.custom li::before{content:attr(data-mk);position:absolute;left:0;color:var(--mkc);font-weight:700}
`;
}

function rfExperienceHtml(cfg, d, P) {
  const style = cfg.experience.style, jobs = d.experience;
  if (style === "timeline") {
    const items = jobs.map(j =>
      `<div class="tl-item"><div class="tl-dot" style="border-color:${P.accent}"></div>` +
      `<div class="tl-body"><div class="tl-head"><span class="tl-role">${rfEsc(j.role)}</span>` +
      `<span class="tl-period">${rfEsc(j.period)}</span></div>` +
      `<div class="tl-co" style="color:${P.accent}">${rfEsc(j.company)} · ${rfEsc(j.location)}</div>` +
      `${rfBulletsHtml(j.bullets, cfg, P)}</div></div>`).join("");
    return `<div class="tl" style="--tlc:${P.rule}">${items}</div>`;
  }
  if (style === "card") {
    const items = jobs.map(j =>
      `<div class="job-card" style="border-color:${P.rule}">` +
      `<div class="jc-head"><span class="jc-role">${rfEsc(j.role)}</span>` +
      `<span class="jc-period">${rfEsc(j.period)}</span></div>` +
      `<div class="jc-co" style="color:${P.accent}">${rfEsc(j.company)} · ${rfEsc(j.location)}</div>` +
      `${rfBulletsHtml(j.bullets, cfg, P)}</div>`).join("");
    return `<div class="job-cards">${items}</div>`;
  }
  const items = jobs.map(j =>
    `<div class="job"><div class="job-head"><span class="job-role">${rfEsc(j.role)}</span>` +
    `<span class="job-period">${rfEsc(j.period)}</span></div>` +
    `<div class="job-co" style="color:${P.accent}">${rfEsc(j.company)} · ${rfEsc(j.location)}</div>` +
    `${rfBulletsHtml(j.bullets, cfg, P)}</div>`).join("");
  return `<div class="jobs">${items}</div>`;
}

function rfExperienceCss(P) {
  return `
.jobs{display:grid;gap:14px}.job-head,.jc-head,.tl-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.job-role,.jc-role,.tl-role{font-weight:700;font-size:14px}
.job-period,.jc-period,.tl-period{font-size:11.5px;color:${P.muted};white-space:nowrap;font-weight:600}
.job-co,.jc-co,.tl-co{font-size:12.5px;font-weight:600;margin:2px 0 2px}
.job-cards{display:grid;gap:12px}.job-card{border:1px solid;border-radius:8px;padding:14px 16px}
.tl{position:relative;padding-left:26px}.tl::before{content:"";position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:var(--tlc)}
.tl-item{position:relative;margin-bottom:16px}.tl-item:last-child{margin-bottom:0}
.tl-dot{position:absolute;left:-26px;top:5px;width:16px;height:16px;border-radius:50%;background:#fff;border:3px solid}
`;
}

function rfEducationHtml(d) {
  return d.education.map(e =>
    `<div class="edu"><div class="edu-head"><span class="edu-deg">${rfEsc(e.degree)}</span>` +
    `<span class="edu-period">${rfEsc(e.period)}</span></div>` +
    `<div class="edu-school">${rfEsc(e.school)}</div>` +
    (e.detail ? `<div class="edu-detail">${rfEsc(e.detail)}</div>` : "") + `</div>`).join("");
}

function rfSectionBlock(cfg, key, d, P, idx) {
  const titles = { summary: "Profile", experience: "Experience", skills: "Skills", education: "Education", projects: "Projects", certifications: "Certifications", languages: "Languages" };
  const t = rfSectionTitle(cfg, titles[key], idx);
  let body = "";
  if (key === "summary") body = `<p class="summary">${rfEsc(d.summary)}</p>`;
  else if (key === "experience") body = rfExperienceHtml(cfg, d, P);
  else if (key === "skills") body = rfSkillsHtml(cfg, d.skills, P);
  else if (key === "education") body = `<div class="edus">${rfEducationHtml(d)}</div>`;
  else if (key === "projects") body = `<div class="projs">${d.projects.map(p =>
    `<div class="proj"><span class="proj-name">${rfEsc(p.name)}</span><span class="proj-sep"> — </span><span class="proj-det">${rfEsc(p.detail)}</span></div>`).join("")}</div>`;
  else if (key === "certifications") body = `<ul class="certs">${d.certifications.map(c => `<li>${rfEsc(c)}</li>`).join("")}</ul>`;
  else body = `<p class="langs">${d.languages.map(l => rfEsc(l)).join(" &nbsp;·&nbsp; ")}</p>`;
  return `<section class="sec">${t}${body}</section>`;
}

function rfSectionsCss(P) {
  return `
.summary{font-size:13.2px}
.edus{display:grid;gap:10px}.edu-head{display:flex;justify-content:space-between;gap:12px}
.edu-deg{font-weight:700;font-size:13.5px}.edu-period{font-size:11.5px;color:${P.muted};font-weight:600;white-space:nowrap}
.edu-school{font-size:12.5px;color:${P.accent};font-weight:600}.edu-detail{font-size:12px;color:${P.muted}}
.projs{display:grid;gap:8px;font-size:12.8px}.proj-name{font-weight:700}
.certs{list-style:none;display:grid;gap:5px;font-size:12.8px}.certs li::before{content:"✓ ";color:${P.accent};font-weight:700}
.langs{font-size:12.8px}
`;
}

function rfPageShapeHtml(cfg, P) {
  const s = cfg.accents.page_shape;
  if (s === "diagonal") return `<div class="shape" style="position:absolute;top:0;right:0;width:220px;height:220px;background:${P.accent};clip-path:polygon(100% 0,0 0,100% 100%);opacity:.14"></div>`;
  if (s === "wave") return `<svg class="shape" style="position:absolute;top:0;left:0;width:100%;height:90px" viewBox="0 0 794 90" preserveAspectRatio="none"><path d="M0 0h794v38c-120 30-260 30-397 0S120 50 0 62z" fill="${P.accent}" opacity=".16"/></svg>`;
  if (s === "arch") return `<div class="shape" style="position:absolute;top:-70px;left:50%;transform:translateX(-50%);width:560px;height:280px;background:${P.accent};opacity:.12;border-radius:0 0 280px 280px"></div>`;
  if (s === "corners") {
    const c = P.accent;
    return `<div class="shape corners"><i style="top:14px;left:14px;border-top:5px solid ${c};border-left:5px solid ${c}"></i>` +
      `<i style="top:14px;right:14px;border-top:5px solid ${c};border-right:5px solid ${c}"></i>` +
      `<i style="bottom:14px;left:14px;border-bottom:5px solid ${c};border-left:5px solid ${c}"></i>` +
      `<i style="bottom:14px;right:14px;border-bottom:5px solid ${c};border-right:5px solid ${c}"></i></div>` +
      `<style>.corners i{position:absolute;width:56px;height:56px}</style>`;
  }
  if (s === "dots") return `<div class="shape" style="position:absolute;top:0;right:0;width:260px;height:180px;opacity:.5;background-image:radial-gradient(${P.accent} 1.6px,transparent 1.6px);background-size:18px 18px;mask-image:linear-gradient(to bottom left,#000,transparent)}"></div>`;
  return "";
}

/* ---- layouts ---- */

function rfLayoutClassic(cfg, d, P) {
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page">${rfPageShapeHtml(cfg, P)}<div class="pad">${rfHeaderHtml(cfg, d, P)}${secs}</div></div>`;
}

function rfLayoutSidebar(cfg, d, P, side) {
  const S = cfg.sidebar;
  const order = cfg.sections.order.filter(k => k !== "skills");
  const mainSecs = order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  const contactItems = [[RF_ICONS.mail, d.email], [RF_ICONS.phone, d.phone], [RF_ICONS.pin, d.location], [RF_ICONS.web, d.website], [RF_ICONS.link, d.linkedin]];
  const sideContact = contactItems.map(([ic, v]) => `<div class="s-c"><span class="s-ic">${ic}</span><span>${rfEsc(v)}</span></div>`).join("");
  const df = cfg.fonts.display, photo = rfPhotoHtml(cfg, d, P);
  const aside =
    `<aside class="sb" style="background:${S.bg};color:${S.ink}">` + photo +
    `<div class="s-sec"><div class="s-h" style="color:${S.accent}">Contact</div>${sideContact}</div>` +
    `<div class="s-sec"><div class="s-h" style="color:${S.accent}">Skills</div>` +
    rfSkillsHtml(cfg, d.skills, { ink: S.ink, accent: S.accent, muted: S.muted, rule: "rgba(128,128,128,.35)" }) + `</div>` +
    `<div class="s-sec"><div class="s-h" style="color:${S.accent}">Languages</div>` +
    `<div class="s-list">${d.languages.map(l => rfEsc(l)).join("<br>")}</div></div>` +
    `<div class="s-sec"><div class="s-h" style="color:${S.accent}">Certifications</div>` +
    `<div class="s-list">${d.certifications.map(c => rfEsc(c)).join("<br>")}</div></div>` +
    `</aside>`;
  const head = `<div class="sb-head"><div class="sb-name" style="font-family:'${df}',serif">${rfEsc(d.name)}</div>` +
    `<div class="sb-title" style="color:${P.accent}">${rfEsc(d.title)}</div></div>`;
  const main = `<main class="sb-main"><div class="pad">${head}${mainSecs}</div></main>`;
  const inner = side === "left" ? aside + main : main + aside;
  return `<div class="page"><div class="sb-wrap">${inner}</div></div>`;
}

function rfSidebarCss() {
  return `
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
`;
}

function rfLayoutBanner(cfg, d, P) {
  const df = cfg.fonts.display, photo = rfPhotoHtml(cfg, d, P);
  const banner = `<div class="bnr" style="background:${P.accent};color:#fff">${photo}<div>` +
    `<div class="bnr-name" style="font-family:'${df}',serif">${rfEsc(d.name)}</div>` +
    `<div class="bnr-title">${rfEsc(d.title)}</div>${rfContactRow(d, "#fff")}</div></div>`;
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page">${banner}<div class="pad">${secs}</div></div>`;
}

function rfBannerCss() {
  return `
.bnr{display:flex;gap:24px;align-items:center;padding:40px 46px}
.bnr .photo{background:rgba(255,255,255,.22)!important}
.bnr-name{font-size:38px;font-weight:800;line-height:1.1}
.bnr-title{font-size:15px;font-weight:600;letter-spacing:.1em;margin-top:6px;opacity:.92}
.bnr .contact{color:#fff}.bnr .c-ic{color:#fff}
`;
}

function rfLayoutTimeline(cfg, d, P) {
  const cfg2 = Object.assign({}, cfg, { experience: { style: "timeline" } });
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg2, k, d, P, i)).join("");
  return `<div class="page">${rfPageShapeHtml(cfg, P)}<div class="pad">${rfHeaderHtml(cfg, d, P)}${secs}</div></div>`;
}

function rfLayoutEditorial(cfg, d, P) {
  const df = cfg.fonts.display, photo = rfPhotoHtml(cfg, d, P);
  const head = `<header class="ed-head">${photo}<div class="ed-name" style="font-family:'${df}',serif">${rfEsc(d.name)}</div>` +
    `<div class="ed-title" style="color:${P.accent}">${rfEsc(d.title)} &nbsp;·&nbsp; ${rfEsc(d.location)}</div>` +
    `<div class="ed-rule" style="background:${P.accent}"></div>${rfContactRow(d)}</header>`;
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page"><div class="pad ed">${head}${secs}</div></div>`;
}

function rfEditorialCss() {
  return `
.ed-head{margin-bottom:24px}.ed-head .photo{margin-bottom:14px}
.ed-name{font-size:44px;font-weight:700;line-height:1.05;letter-spacing:-.01em}
.ed-title{font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;margin:8px 0 12px}
.ed-rule{width:72px;height:5px;margin-bottom:12px}
.ed .sec p.summary{font-size:14.5px;line-height:1.75}
.ed .jobs{columns:2;column-gap:28px}.ed .job{break-inside:avoid;margin-bottom:16px}
`;
}

function rfLayoutCards(cfg, d, P) {
  const cfg2 = Object.assign({}, cfg, { experience: { style: "card" } });
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg2, k, d, P, i)).join("");
  return `<div class="page">${rfPageShapeHtml(cfg, P)}<div class="pad">${rfHeaderHtml(cfg, d, P)}${secs}</div></div>`;
}

function rfLayoutSwiss(cfg, d, P) {
  const cells = [["Name", d.name], ["Title", d.title], ["Mail", d.email], ["Phone", d.phone], ["Place", d.location], ["Web", d.website]];
  const grid = cells.map(([k, v]) => `<div class="sw-cell"><div class="sw-k">${k}</div><div class="sw-v">${rfEsc(v)}</div></div>`).join("");
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page"><div class="pad"><div class="sw-grid" style="border-color:${P.rule}">${grid}</div>` +
    `<div class="sw-rule" style="background:${P.ink}"></div>${secs}</div></div>`;
}

function rfSwissCss(P) {
  return `
.sw-grid{display:grid;grid-template-columns:1fr 1fr 1fr;border-top:1px solid;border-bottom:1px solid;margin-bottom:6px}
.sw-cell{padding:10px 12px;border-right:1px solid ${P.rule}}
.sw-cell:nth-child(3n){border-right:none}
.sw-k{font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:${P.muted};font-weight:700}
.sw-v{font-size:13px;font-weight:600;margin-top:2px}
.sw-rule{height:3px;margin:14px 0 22px}
`;
}

function rfLayoutCreative(cfg, d, P) {
  const df = cfg.fonts.display, photo = rfPhotoHtml(cfg, d, P);
  const head = `<header class="cr-head"><div class="cr-geo" style="background:${P.accent2}"></div><div>` +
    `<div class="cr-kicker" style="color:${P.accent}">Résumé — ${rfEsc(d.title)}</div>` +
    `<div class="cr-name" style="font-family:'${df}',serif">${rfEsc(d.name)}</div></div>${photo}</header>`;
  const secs = cfg.sections.order.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page"><div class="pad">${head}${secs}</div></div>`;
}

function rfCreativeCss() {
  return `
.cr-head{display:flex;align-items:center;gap:20px;margin-bottom:26px;position:relative}
.cr-geo{position:absolute;left:-46px;top:-10px;width:14px;height:120px;transform:skewX(-12deg)}
.cr-kicker{font-size:11px;font-weight:800;letter-spacing:.26em;text-transform:uppercase;margin-bottom:8px}
.cr-name{font-size:52px;font-weight:800;line-height:1;letter-spacing:-.015em}
.cr-head .photo{margin-left:auto}
`;
}

function rfLayoutCompact(cfg, d, P) {
  const df = cfg.fonts.display;
  const head = `<header class="cp-head"><div><div class="cp-name" style="font-family:'${df}',serif">${rfEsc(d.name)}</div>` +
    `<div class="cp-title" style="color:${P.accent}">${rfEsc(d.title)}</div></div>` +
    `<div class="cp-contact">${rfEsc(d.email)} · ${rfEsc(d.phone)}<br>${rfEsc(d.location)} · ${rfEsc(d.website)}</div></header>`;
  const mainKeys = cfg.sections.order.filter(k => ["summary", "experience", "projects"].includes(k));
  const sideKeys = cfg.sections.order.filter(k => ["skills", "education", "certifications", "languages"].includes(k));
  const main = mainKeys.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  const side = sideKeys.map((k, i) => rfSectionBlock(cfg, k, d, P, i)).join("");
  return `<div class="page"><div class="pad"><div class="cp-wrap"><div class="cp-main">${head}${main}</div>` +
    `<div class="cp-side" style="border-color:${P.rule}">${side}</div></div></div></div>`;
}

function rfCompactCss(P) {
  return `
.cp-wrap{display:grid;grid-template-columns:1.9fr 1fr;gap:26px}
.cp-side{border-left:1px solid;padding-left:20px}
.cp-head{margin-bottom:16px}
.cp-name{font-size:26px;font-weight:800}
.cp-title{font-size:13px;font-weight:700;letter-spacing:.06em;margin-top:2px}
.cp-contact{font-size:10.5px;color:${P.muted};margin-top:8px;line-height:1.7}
`;
}

const RF_LAYOUTS = {
  "classic": rfLayoutClassic,
  "sidebar-left": (c, d, p) => rfLayoutSidebar(c, d, p, "left"),
  "sidebar-right": (c, d, p) => rfLayoutSidebar(c, d, p, "right"),
  "banner": rfLayoutBanner,
  "timeline": rfLayoutTimeline,
  "editorial": rfLayoutEditorial,
  "cards": rfLayoutCards,
  "swiss": rfLayoutSwiss,
  "creative": rfLayoutCreative,
  "compact": rfLayoutCompact
};

/* ---- render entry ---- */
function renderTemplate(cfg, data) {
  const P = cfg.page;
  const css = rfBaseCss(cfg, P) + rfSectionTitleCss(cfg, P) + rfSkillsCss(P) +
    rfHeaderCss(P) + rfBulletsCss() + rfExperienceCss(P) + rfSectionsCss(P) +
    rfSidebarCss() + rfBannerCss() + rfEditorialCss() + rfSwissCss(P) +
    rfCreativeCss() + rfCompactCss(P);
  const body = RF_LAYOUTS[cfg.layout](cfg, data, P);
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${rfEsc(cfg.name)} — Resume Template</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="${rfFontHref(cfg.fonts)}" rel="stylesheet">
<style>${css}</style>
</head>
<body>
${body}
</body>
</html>`;
}

const RF_RENDER = { renderTemplate: renderTemplate };
if (typeof window !== "undefined") window.RF_RENDER = RF_RENDER;
if (typeof module !== "undefined" && module.exports) module.exports = RF_RENDER;
