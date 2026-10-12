/* ResumeForge gallery logic */
(function () {
  "use strict";
  const grid = document.getElementById("grid");
  const q = document.getElementById("q");
  const layoutSel = document.getElementById("layout");
  const sortSel = document.getElementById("sort");
  const chipsEl = document.getElementById("chips");
  const countEl = document.getElementById("count");

  let registry = [];
  let activeTag = "";
  const LAYOUTS = ["banner", "cards", "classic", "compact", "creative", "editorial", "sidebar-left", "sidebar-right", "swiss", "timeline", "bespoke"];
  const LAY_LABEL = {
    "banner": "Banner", "cards": "Cards", "classic": "Classic", "compact": "Compact",
    "creative": "Creative", "editorial": "Editorial", "sidebar-left": "Sidebar left",
    "sidebar-right": "Sidebar right", "swiss": "Swiss", "timeline": "Timeline",
    "bespoke": "Bespoke"
  };

  LAYOUTS.forEach(l => {
    const o = document.createElement("option");
    o.value = l; o.textContent = LAY_LABEL[l];
    layoutSel.appendChild(o);
  });

  function topTags(reg, n) {
    const freq = {};
    reg.forEach(t => (t.tags || []).forEach(tag => { freq[tag] = (freq[tag] || 0) + 1; }));
    return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, n).map(e => e[0]);
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  /* Live-rendered preview: the template config + sample data go through the
     JS port of the Python renderer, straight into the iframe's srcdoc. */
  function previewSrc(t) {
    try {
      const data = ((window.RF_SAMPLES || {})[t.sample]) || {};
      return window.renderTemplate(t, data);
    } catch (e) { return ""; }
  }

  function cardEl(t, i) {
    const art = document.createElement("article");
    art.className = "card";
    const no = String(i + 1).padStart(3, "0");
    const lay = LAY_LABEL[t.layout] || t.layout;
    art.innerHTML =
      `<a href="builder.html?template=${encodeURIComponent(t.slug)}" aria-label="Open ${esc(t.name)} in the builder">` +
      `<div class="preview"></div>` +
      `<div class="card-body"><div class="card-no">№ ${no}</div><h3>${esc(t.name)}</h3>` +
      `<p class="persona">${esc(t.persona)}</p>` +
      `<div class="card-tags"><span class="lay">${esc(lay)}</span>` +
      (t.tags || []).slice(0, 3).map(tag => `<span>${esc(tag)}</span>`).join("") +
      `</div></div></a>`;
    const f = document.createElement("iframe");
    f.setAttribute("loading", "lazy");
    f.setAttribute("scrolling", "no");
    f.setAttribute("title", t.name + " preview");
    if (t.bespoke && t.file) f.src = t.file;
    else f.srcdoc = previewSrc(t);
    art.querySelector(".preview").appendChild(f);
    return art;
  }

  /* Scale each 794px-wide preview to its card width. */
  function fitPreviews() {
    document.querySelectorAll(".preview").forEach(pv => {
      const s = pv.clientWidth / 794;
      const f = pv.querySelector("iframe");
      if (f) f.style.transform = "scale(" + s + ")";
    });
  }

  function filtered() {
    const term = q.value.trim().toLowerCase();
    const lay = layoutSel.value;
    let list = registry.filter(t => {
      if (lay && t.layout !== lay) return false;
      if (activeTag && !(t.tags || []).includes(activeTag)) return false;
      if (term) {
        const hay = (t.name + " " + t.persona + " " + t.layout + " " + (t.tags || []).join(" ")).toLowerCase();
        if (!hay.includes(term)) return false;
      }
      return true;
    });
    if (sortSel.value === "az") list = list.slice().sort((a, b) => a.name.localeCompare(b.name));
    return list;
  }

  function render() {
    const list = filtered();
    grid.innerHTML = "";
    if (!list.length) {
      grid.innerHTML = `<div class="empty"><h3>Nothing matches.</h3><p>Try a different search or clear the filters.</p></div>`;
    } else {
      list.forEach((t, i) => grid.appendChild(cardEl(t, i)));
    }
    countEl.innerHTML = `Showing <strong>${list.length}</strong> of ${registry.length}`;
    fitPreviews();
  }

  let deb = null;
  q.addEventListener("input", () => { clearTimeout(deb); deb = setTimeout(render, 160); });
  layoutSel.addEventListener("change", render);
  sortSel.addEventListener("change", render);
  window.addEventListener("resize", fitPreviews);

  fetch("registry.json")
    .then(r => { if (!r.ok) throw new Error("registry " + r.status); return r.json(); })
    .then(reg => {
      registry = reg;
      topTags(reg, 14).forEach(tag => {
        const b = document.createElement("button");
        b.className = "chip"; b.textContent = tag;
        b.addEventListener("click", () => {
          activeTag = activeTag === tag ? "" : tag;
          document.querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c.textContent === activeTag));
          render();
        });
        chipsEl.appendChild(b);
      });
      render();
    })
    .catch(err => {
      grid.innerHTML = `<div class="empty"><h3>Could not load the library.</h3><p>${String(err).replace(/</g, "&lt;")}</p></div>`;
    });
})();
