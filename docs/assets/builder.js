/* ResumeForge builder logic */
(function () {
  "use strict";
  const $ = id => document.getElementById(id);
  const tplSel = $("tpl"), tplInfo = $("tplInfo"), frame = $("preview");
  const form = $("form");

  let registry = [];
  let current = null;

  /* ---- dynamic repeatable fields ---- */
  function buildExp() {
    const wrap = $("expWrap");
    for (let n = 0; n < 3; n++) {
      const div = document.createElement("div");
      div.className = "exp-entry";
      div.innerHTML =
        `<div class="en">Position ${n + 1}</div>` +
        `<div class="field"><label>Role</label><input data-exp="${n}" data-f="role"></div>` +
        `<div class="field"><label>Company</label><input data-exp="${n}" data-f="company"></div>` +
        `<div class="field"><label>Period</label><input data-exp="${n}" data-f="period" placeholder="2022 — Present"></div>` +
        `<div class="field"><label>Location</label><input data-exp="${n}" data-f="location"></div>` +
        `<div class="field"><label>Achievements</label><textarea data-exp="${n}" data-f="bullets" rows="3"></textarea></div>`;
      wrap.appendChild(div);
    }
  }
  function buildEdu() {
    const wrap = $("eduWrap");
    for (let n = 0; n < 2; n++) {
      const div = document.createElement("div");
      div.className = "exp-entry";
      div.innerHTML =
        `<div class="en">Education ${n + 1}</div>` +
        `<div class="field"><label>Degree</label><input data-edu="${n}" data-f="degree"></div>` +
        `<div class="field"><label>School</label><input data-edu="${n}" data-f="school"></div>` +
        `<div class="field"><label>Period</label><input data-edu="${n}" data-f="period"></div>` +
        `<div class="field"><label>Detail</label><input data-edu="${n}" data-f="detail"></div>`;
      wrap.appendChild(div);
    }
  }
  buildExp(); buildEdu();

  /* ---- data collection ---- */
  const lines = v => v.split("\n").map(s => s.trim()).filter(Boolean);

  function collectData() {
    const val = k => { const el = form.querySelector(`[data-k="${k}"]`); return el ? el.value.trim() : ""; };
    const data = {
      name: val("name") || "Your Name", title: val("title") || "Professional Title",
      email: val("email"), phone: val("phone"), location: val("location"),
      website: val("website"), linkedin: val("linkedin"),
      summary: val("summary"), experience: [], education: [],
      skills: [], projects: [], certifications: [], languages: []
    };
    for (let n = 0; n < 3; n++) {
      const get = f => { const el = form.querySelector(`[data-exp="${n}"][data-f="${f}"]`); return el ? el.value.trim() : ""; };
      if (!get("role")) continue;
      data.experience.push({
        role: get("role"), company: get("company"), period: get("period"),
        location: get("location"), bullets: lines(get("bullets"))
      });
    }
    for (let n = 0; n < 2; n++) {
      const get = f => { const el = form.querySelector(`[data-edu="${n}"][data-f="${f}"]`); return el ? el.value.trim() : ""; };
      if (!get("degree")) continue;
      data.education.push({ degree: get("degree"), school: get("school"), period: get("period"), detail: get("detail") });
    }
    data.skills = lines($("f_skills").value).map(l => {
      const m = l.match(/^(.*?):\s*(\d+)\s*$/);
      if (m) return { name: m[1].trim(), level: Math.max(0, Math.min(100, parseInt(m[2], 10))) };
      return { name: l, level: 70 };
    });
    data.projects = lines($("f_projects").value).map(l => {
      const i = l.indexOf("|");
      return i === -1 ? { name: l, detail: "" } : { name: l.slice(0, i).trim(), detail: l.slice(i + 1).trim() };
    });
    data.certifications = lines($("f_certs").value);
    data.languages = lines($("f_langs").value);
    return data;
  }

  /* ---- render ---- */
  let timer = null;
  function render() {
    if (!current || !window.RF_RENDER) return;
    try {
      frame.srcdoc = window.RF_RENDER.renderTemplate(current, collectData());
    } catch (e) { /* keep last good preview on bad input */ }
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 220); }
  form.addEventListener("input", schedule);

  /* ---- sample data ---- */
  function fillForm(d) {
    const set = (k, v) => { const el = form.querySelector(`[data-k="${k}"]`); if (el) el.value = v || ""; };
    ["name", "title", "email", "phone", "location", "website", "linkedin", "summary"].forEach(k => set(k, d[k]));
    (d.experience || []).slice(0, 3).forEach((j, n) => {
      ["role", "company", "period", "location"].forEach(f => {
        const el = form.querySelector(`[data-exp="${n}"][data-f="${f}"]`); if (el) el.value = j[f] || "";
      });
      const b = form.querySelector(`[data-exp="${n}"][data-f="bullets"]`);
      if (b) b.value = (j.bullets || []).join("\n");
    });
    (d.education || []).slice(0, 2).forEach((e, n) => {
      ["degree", "school", "period", "detail"].forEach(f => {
        const el = form.querySelector(`[data-edu="${n}"][data-f="${f}"]`); if (el) el.value = e[f] || "";
      });
    });
    $("f_skills").value = (d.skills || []).map(s => `${s.name}:${s.level}`).join("\n");
    $("f_projects").value = (d.projects || []).map(p => `${p.name} | ${p.detail}`).join("\n");
    $("f_certs").value = (d.certifications || []).join("\n");
    $("f_langs").value = (d.languages || []).join("\n");
  }

  $("sampleBtn").addEventListener("click", () => {
    if (!current || !window.RF_SAMPLES) return;
    const d = window.RF_SAMPLES[current.sample || "engineer"];
    if (d) { fillForm(d); render(); }
  });

  $("printBtn").addEventListener("click", () => {
    try { frame.contentWindow.focus(); frame.contentWindow.print(); }
    catch (e) { alert("Could not open the print dialog for the preview."); }
  });

  /* ---- template select ---- */
  function selectTemplate(slug) {
    current = registry.find(t => t.slug === slug) || registry[0];
    if (!current) return;
    tplSel.value = current.slug;
    tplInfo.innerHTML = `<strong>${current.name}</strong> — ${current.persona} · ${(current.tags || []).join(", ")}`;
    render();
  }
  tplSel.addEventListener("change", () => selectTemplate(tplSel.value));

  fetch("registry.json")
    .then(r => { if (!r.ok) throw new Error("registry " + r.status); return r.json(); })
    .then(reg => {
      registry = reg;
      reg.forEach(t => {
        const o = document.createElement("option");
        o.value = t.slug; o.textContent = `${t.name} — ${t.persona}`;
        tplSel.appendChild(o);
      });
      const slug = new URLSearchParams(location.search).get("template");
      selectTemplate(slug && reg.some(t => t.slug === slug) ? slug : reg[0].slug);
      /* Start with sample data so the preview is alive immediately. */
      if (window.RF_SAMPLES && current) {
        const d = window.RF_SAMPLES[current.sample || "engineer"];
        if (d) fillForm(d);
        render();
      }
    })
    .catch(() => { tplInfo.textContent = "Could not load the template library."; });
})();
