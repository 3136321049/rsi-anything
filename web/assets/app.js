const BASE = new URL("../", import.meta.url);
const body = document.body;
const page = body.dataset.page;
const lang = body.dataset.lang === "zh" ? "zh" : "en";
const HOME = new URL(body.dataset.home || "./", location.href);
const T = JSON.parse(document.getElementById("i18n")?.textContent || "{}");
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const url = path => new URL(path, BASE).href;
const home = path => new URL(path, HOME).href;
const locale = lang === "zh" ? "zh-CN" : "en-US";
const number = value => value == null ? "—" : Number(value).toLocaleString(locale, { maximumFractionDigits: 3 });
const clock = seconds => `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const unitText = unit => /^[A-Za-z]/.test(unit || "") ? " " + unit : unit || "";
// 模板与案例说明：中文页读 README.md，英文页读 README.en.md。
const guide = folder => `${folder}/${lang === "zh" ? "README.md" : "README.en.md"}`;

function t(key, vars) {
  const value = key.split(".").reduce((node, part) => node?.[part], T);
  if (typeof value !== "string") { console.warn("missing text", key); return key; }
  return vars ? value.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "") : value;
}
const status = code => T.status?.[code] ?? code;
const roundName = n => n ? t("round", { n }) : t("baseline");
const stateClass = s => s === "KEEP" ? "keep" : s === "REVERT" ? "revert" : s?.endsWith("FAIL") ? "fail" : s === "BASELINE" ? "base" : "";

/* ---------- shared chrome ---------- */
let toastTimer;
function toast(message) {
  const box = $("#toast");
  box.textContent = message;
  box.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => box.classList.remove("visible"), 2800);
}
async function copy(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
    else {
      const input = document.createElement("textarea");
      input.value = text; input.style.cssText = "position:fixed;left:-9999px";
      document.body.append(input); input.select();
      const ok = document.execCommand("copy"); input.remove();
      if (!ok) throw new Error("copy");
    }
    toast(t("copied"));
  } catch { toast(t("copy_failed")); }
}
const dialog = $("#media-dialog");
let dialogFocus;
function openDialog(title, content, wide = false) {
  dialogFocus = document.activeElement;
  $("#dialog-title").textContent = title;
  $("#dialog-content").innerHTML = content;
  dialog.classList.toggle("wide", wide);
  dialog.showModal();
}
function closeDialog() {
  $$("video", dialog).forEach(v => v.pause());
  dialog.close();
  $("#dialog-content").replaceChildren();
  dialogFocus?.focus?.();
}
$(".close-dialog").addEventListener("click", closeDialog);
dialog.addEventListener("click", e => { if (e.target === dialog) closeDialog(); });
dialog.addEventListener("cancel", e => { e.preventDefault(); closeDialog(); });

const header = $(".site-header"), nav = $("#main-nav"), toggle = $(".menu-toggle");
function setMenu(open) {
  nav.classList.toggle("open", open);
  header.classList.toggle("menu-open", open);
  toggle.setAttribute("aria-expanded", String(open));
  toggle.setAttribute("aria-label", open ? t("nav_close") : t("nav_open"));
}
toggle.addEventListener("click", () => setMenu(!nav.classList.contains("open")));
$$("a", nav).forEach(a => a.addEventListener("click", () => setMenu(false)));
document.addEventListener("keydown", e => { if (e.key === "Escape") setMenu(false); });
addEventListener("scroll", () => header.classList.toggle("scrolled", scrollY > 8), { passive: true });
$$(`[data-nav="${page === "start" ? "start" : page === "cases" ? "cases" : ""}"]`).forEach(a => a.setAttribute("aria-current", "page"));

// 深浅主题：默认跟随系统；访客点过就记住选择（<head> 里的小脚本在首帧前恢复）。
const themeButton = $(".theme-toggle");
const systemDark = matchMedia("(prefers-color-scheme: dark)");
const currentTheme = () => document.documentElement.dataset.theme || (systemDark.matches ? "dark" : "light");
function paintTheme() {
  if (!themeButton) return;
  const mode = currentTheme(), label = mode === "dark" ? t("theme_to_light") : t("theme_to_dark");
  themeButton.dataset.mode = mode;
  themeButton.setAttribute("aria-label", label);
  themeButton.title = label;
}
themeButton?.addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("darwin-theme", next); } catch { /* 无痕模式 */ }
  paintTheme();
});
systemDark.addEventListener?.("change", paintTheme);
paintTheme();

function remember(choice) { try { localStorage.setItem("darwin-lang", choice); } catch { /* 无痕模式 */ } }
$$("[data-lang-switch]").forEach(a => a.addEventListener("click", () => {
  remember(a.dataset.langSwitch);
  a.href = a.href.split(/[?#]/)[0] + location.search + location.hash;
}));
(function suggestLanguage() {
  let saved = null;
  try { saved = localStorage.getItem("darwin-lang"); } catch { /* 无痕模式 */ }
  if (saved || lang !== "en" || !/^zh\b/i.test(navigator.language || "")) return;
  const link = $(".nav-lang");
  if (!link) return;
  const bar = document.createElement("div");
  bar.className = "lang-hint";
  bar.innerHTML = `<span lang="zh-CN">${esc(t("lang_hint"))}</span><a lang="zh-CN" href="${esc(link.href)}">${esc(t("lang_hint_go"))}</a><button aria-label="${esc(t("dialog_close"))}">×</button>`;
  $("a", bar).addEventListener("click", e => { remember("zh"); e.currentTarget.href = link.href.split(/[?#]/)[0] + location.search + location.hash; });
  $("button", bar).addEventListener("click", () => { remember("en"); bar.remove(); });
  document.body.append(bar);
})();

$$("[data-wheel-url]").forEach(span => { span.textContent = url("dist/" + span.textContent.trim().split("/").pop()); });

document.addEventListener("click", async e => {
  const button = e.target.closest("[data-copy],[data-copy-target],[data-demo],[data-doc],[data-image]");
  if (!button) return;
  if (button.hasAttribute("data-copy")) await copy(button.dataset.copy);
  else if (button.dataset.copyTarget) await copy($("#" + button.dataset.copyTarget).textContent.replace(/^\$ /gm, ""));
  else if (button.hasAttribute("data-demo")) {
    openDialog(t("demo_title"), `<video controls autoplay muted playsinline preload="metadata" poster="${url("assets/demo-poster.jpg")}" src="${url("examples/showcase-media/openrsi-demo.mp4")}"></video><p class="subtle">${esc(t("demo_caption"))} <a href="${url("examples/showcase-media/demo-video.json")}" target="_blank" rel="noopener">${esc(t("demo_sources"))} ↗</a></p>`, true);
  } else if (button.dataset.image) openDialog(button.dataset.title || t("image"), `<img src="${esc(button.dataset.image)}" alt="${esc(button.dataset.title || t("image"))}">`, true);
  else if (button.dataset.doc) await showDoc(button.dataset.doc);
});
document.addEventListener("play", e => { if (e.target.tagName === "VIDEO") $$("video").forEach(v => { if (v !== e.target) v.pause(); }); }, true);
document.addEventListener("error", e => {
  if (e.target.tagName === "VIDEO" && !e.target.nextElementSibling?.classList.contains("video-error")) {
    const note = document.createElement("p"); note.className = "video-error subtle"; note.textContent = t("video_error");
    e.target.after(note);
  }
}, true);

/* ---------- markdown documents ---------- */
function docInline(text, docPath) {
  const value = esc(text).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    let target;
    try { target = new URL(href.replace(/&amp;/g, "&"), url(docPath)); } catch { return label; }
    if (!["https:", "http:"].includes(target.protocol)) return label;
    const local = target.origin === BASE.origin && target.pathname.startsWith(BASE.pathname);
    const path = local ? decodeURIComponent(target.pathname.slice(BASE.pathname.length)) : "";
    if (local && path.endsWith(".md")) return (T.public_docs || []).includes(path) ? `<button class="inline-link" data-doc="${esc(path)}">${label}</button>` : label;
    return `<a href="${esc(target.href)}" target="_blank" rel="noopener">${label}</a>`;
  });
}
function markdown(text, path) {
  const lines = text.replace(/\r/g, "").split("\n");
  let html = "", fence = false, code = [], table = [], list = [];
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.filter(line => !/^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(line));
    html += `<div class="table-scroll"><table>${rows.map((line, i) => "<tr>" + line.replace(/^\s*\||\|\s*$/g, "").split("|").map(cell => `<${i ? "td" : "th"}>${docInline(cell.trim(), path)}</${i ? "td" : "th"}>`).join("") + "</tr>").join("")}</table></div>`;
    table = [];
  };
  const flushList = () => { if (list.length) html += `<ul>${list.map(item => `<li>${docInline(item, path)}</li>`).join("")}</ul>`; list = []; };
  for (const line of lines) {
    if (line.startsWith("```")) { flushTable(); flushList(); if (fence) { html += `<pre><code>${esc(code.join("\n"))}</code></pre>`; code = []; } fence = !fence; continue; }
    if (fence) { code.push(line); continue; }
    if (line.trim().startsWith("|")) { flushList(); table.push(line); continue; }
    flushTable();
    if (/^\s*[-*] /.test(line)) { list.push(line.replace(/^\s*[-*] /, "")); continue; }
    flushList();
    const heading = /^(#{1,4}) (.*)/.exec(line);
    if (heading) html += `<h${Math.min(4, heading[1].length + 1)}>${docInline(heading[2], path)}</h${Math.min(4, heading[1].length + 1)}>`;
    else if (line.trim()) html += `<p>${docInline(line, path)}</p>`;
  }
  flushTable(); flushList();
  if (code.length) html += `<pre><code>${esc(code.join("\n"))}</code></pre>`;
  return html;
}
async function showDoc(path) {
  try {
    const response = await fetch(url(path));
    if (!response.ok) throw new Error("missing");
    const text = await response.text();
    openDialog(t("doc_title"), `<div class="document-view">${markdown(text, path)}<a class="raw-doc-link" href="${esc(url(path))}" target="_blank" rel="noopener">${esc(t("doc_raw"))} ↗</a></div>`, true);
  } catch { toast(t("doc_failed")); }
}

/* ---------- home: evolution replay ---------- */
function renderHome() {
  const data = JSON.parse($("#home-data").textContent);
  const panel = $("[data-evo]"), chart = $("#evo-chart"), detail = $("#evo-detail");
  let active = "code-speed", selected = null, timer = null, interacted = false;
  const labPath = { "code-speed": "labs/code/?case=code-speed&", "cpu-classifier": "labs/experiments/?", "video-cut": "labs/video/?", "svg-drawing": "labs/visual/?case=svg-drawing&" };

  function layout(series) {
    const rows = series.rounds;
    const scores = rows.map(r => r.score).filter(v => v != null);
    const lo = Math.min(...scores), hi = Math.max(...scores), pad = (hi - lo) * 0.14 || 1;
    const x = i => 6 + 88 * i / Math.max(1, rows.length - 1);
    const y = v => 86 - 72 * (v - lo + pad * 0.2) / (hi - lo + pad * 1.2);
    let best = rows[0].score, parent = 0;
    return rows.map((row, i) => {
      const point = { row, x: x(i), parentX: x(parent), parentY: y(best), y: row.score == null ? y(best) : y(row.score), best };
      if (row.status === "KEEP") { best = row.score; parent = i; }
      point.champion = y(best);
      return point;
    });
  }
  function draw() {
    const series = data.series[active];
    const points = layout(series);
    let champion = `M ${points[0].x * 10} ${points[0].y}`;
    for (const p of points.slice(1)) champion += ` H ${p.x * 10} V ${p.champion}`;
    const branches = points.filter(p => p.row.status === "REVERT").map(p => `<path class="evo-branch" d="M ${p.parentX * 10} ${p.parentY} C ${(p.parentX + p.x) * 5} ${p.parentY}, ${(p.parentX + p.x) * 5} ${p.y}, ${p.x * 10} ${p.y}" />`).join("");
    const grid = [20, 50, 80].map(v => `<line x1="0" x2="1000" y1="${v}" y2="${v}" />`).join("");
    chart.innerHTML = `<svg class="${reduceMotion ? "" : "reveal"}" viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true"><g class="evo-grid">${grid}</g>${branches}<path class="evo-line" d="${champion}" /></svg>` +
      points.map((p, i) => `<button class="evo-node ${stateClass(p.row.status)} ${p.row.score == null ? "empty" : ""}" style="left:${p.x}%;top:${p.y}%;--i:${i}" data-node="${i}" aria-label="${esc(roundName(p.row.round) + " · " + status(p.row.status) + (p.row.score == null ? "" : " · " + number(p.row.score) + unitText(series.unit)))}"><span class="evo-value">${p.row.score == null ? "—" : number(p.row.score) + esc(unitText(series.unit))}</span></button>`).join("") +
      `<div class="evo-axis">${points.map(p => `<span style="left:${p.x}%">${esc(p.row.label || "R" + p.row.round)}</span>`).join("")}</div>`;
    chart.classList.toggle("dense", points.length > 8);
    $$("[data-node]", chart).forEach(b => b.addEventListener("click", () => { interacted = true; stop(); select(Number(b.dataset.node)); }));
    select(series.rounds.findIndex(r => r.round === series.best_round));
  }
  function select(index) {
    const series = data.series[active], row = series.rounds[index];
    selected = index;
    $$("[data-node]", chart).forEach(b => b.classList.toggle("active", Number(b.dataset.node) === index));
    const best = series.rounds.slice(0, index).reduce((value, r) => (r.round === 0 || r.status === "KEEP") ? r.score : value, null);
    const delta = row.score != null && best != null && index ? row.score - best : null;
    const deltaText = delta == null ? "" : `<span class="evo-delta ${row.status === "KEEP" ? "up" : row.status === "REVERT" ? "down" : ""}">${delta >= 0 ? "+" : "−"}${number(Math.abs(delta))}${esc(unitText(series.unit))} ${esc(t("home.vs_best"))}</span>`;
    const [, runNo, roundNo] = (row.label || "R" + row.round).match(/^(?:(\d+)·)?R(\d+)$/) || [];
    const head = (runNo ? `RUN ${runNo} · ` : "") + (Number(roundNo) ? "ROUND " + roundNo.padStart(2, "0") : "BASELINE");
    detail.innerHTML = `<div class="evo-detail-top"><span class="mono">${head}</span><span class="pill ${stateClass(row.status)}">${esc(status(row.status))}${row.round === series.best_round && row.round ? " · " + esc(status("final")) : ""}</span></div>
      <div class="evo-score">${row.score == null ? "—" : number(row.score)}<small>${row.score == null ? "" : esc(series.unit)}</small></div>
      <div class="evo-metric">${esc(series.metric)} ${deltaText}</div>
      ${row.image ? `<img class="evo-thumb" src="${url(row.image)}" alt="${esc(head)}" width="1024" height="768">` : ""}<p>${esc(row.summary || (row.round ? t("home.no_change") : t("home.baseline_note")))}</p>
      <a class="evo-open" href="${home(labPath[active] + "round=" + row.round)}">${esc(t("home.open_round"))}<span aria-hidden="true">→</span></a>`;
  }
  function stop() { clearInterval(timer); timer = null; }
  function play() {
    if (reduceMotion || interacted || timer) return;
    timer = setInterval(() => {
      const rows = data.series[active].rounds;
      if (selected >= rows.length - 1) {
        const order = Object.keys(data.series), next = order[(order.indexOf(active) + 1) % order.length];
        activate(next); select(0);
      } else select(selected + 1);
    }, 2600);
  }
  function activate(id) {
    active = id;
    $$("[data-evo-tab]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.evoTab === id)));
    draw();
  }
  $$("[data-evo-tab]").forEach(b => b.addEventListener("click", () => { interacted = true; stop(); activate(b.dataset.evoTab); }));
  panel.addEventListener("pointerenter", stop);
  panel.addEventListener("pointerleave", () => { if (!interacted) play(); });
  new IntersectionObserver(entries => entries.forEach(entry => entry.isIntersecting ? play() : stop()), { threshold: 0.3 }).observe(panel);
  activate(active);

  $$("[data-matrix]").forEach(box => {
    const matrix = data.matrices[box.dataset.matrix];
    const peak = Math.max(...matrix.flat());
    box.innerHTML = matrix.flat().map((v, i) => `<i class="${Math.floor(i / 10) === i % 10 ? "diag" : v ? "miss" : ""}" style="--a:${v ? 0.18 + 0.82 * Math.min(1, v / peak) : 0}"></i>`).join("");
  });
  $$("[data-segments]").forEach(strip => {
    const keep = new Set(data.segments.selected);
    strip.innerHTML = Array.from({ length: data.segments.total }, (_, i) => `<i class="${keep.has(i + 1) ? "on" : ""}"></i>`).join("");
  });
}

/* ---------- labs ---------- */
let current, selected = 0, loadId = 0;
const LAB_CASES = { code: ["code-speed", "code-repair"], experiments: ["cpu-classifier"], video: ["video-cut"], visual: ["svg-drawing", "landing-page"] };
const state = { template: LAB_CASES[page]?.[0], mode: "split", compare: "baseline", view: "now" };
const params = new URLSearchParams(location.search);
if (LAB_CASES[page]?.includes(params.get("case"))) state.template = params.get("case");
if (["diff", "split"].includes(params.get("view"))) state.mode = params.get("view");
if (params.get("compare") === "previous") state.compare = "previous";

function syncAddress() {
  const next = new URL(location.href);
  next.search = "";
  if (page === "code" || page === "visual") next.searchParams.set("case", state.template);
  next.searchParams.set("round", selected);
  if (page === "code") {
    if (state.mode !== "split") next.searchParams.set("view", state.mode);
    if (state.compare !== "baseline") next.searchParams.set("compare", state.compare);
  }
  history.replaceState(null, "", next);
}
function pill(row) { return `<span class="pill ${stateClass(row.status)}">${esc(status(row.status))}${row.round === current.best_round && row.round > 0 ? " · " + esc(status("final")) : ""}</span>`; }
function roundNav() {
  return `<div class="round-header"><h2>${esc(t("lab.rounds"))}</h2><span>${esc(t("lab.rounds_hint"))}</span></div><div class="round-nav" role="group" aria-label="${esc(t("lab.rounds"))}">${current.rounds.map(row => `<button class="round-button ${stateClass(row.status)} ${selected === row.round ? "active" : ""}" data-round="${row.round}" aria-pressed="${selected === row.round}"><span>${esc(roundName(row.round))}</span><strong>${number(row.score)}<small>${row.score == null ? "" : esc(current.unit)}</small></strong>${pill(row)}</button>`).join("")}</div>`;
}
function note(row) {
  const title = !row.round ? t("lab.note_baseline") : row.status === "NO_CHANGE" ? t("lab.note_none") : row.status === "REVERT" ? t("lab.note_revert") : t("lab.note_keep");
  return `<div class="callout ${row.status === "REVERT" || !row.formal ? "warning" : ""}"><strong>${esc(title)}</strong><p>${esc(row.hypothesis || t("lab.note_baseline_body"))}</p>${row.note ? `<p>${esc(row.note)}</p>` : ""}${!row.formal ? `<p>${esc(t("lab.note_informal", { n: row.previous_best }))}</p>` : ""}</div>`;
}
function actions() {
  return `<div class="lab-actions"><a class="btn btn-primary" href="${url("downloads/" + current.template + ".zip")}" download>${esc(t("lab.download_all"))}<span aria-hidden="true">↓</span></a><button class="btn btn-ghost" id="share-run">${esc(t("lab.copy_link"))}</button><a class="btn btn-ghost" href="${home("start/?template=" + current.template)}">${esc(t("lab.use_task"))}<span aria-hidden="true">→</span></a></div>`;
}
function evidence() {
  const verification = current.template === "code-speed" ? "artifact-verification.json" : "verification.json";
  return `<div class="evidence-section"><details><summary>${esc(t("lab.scope"))}</summary><div class="evidence-body"><p>${esc(t("lab.limits." + current.template))}</p><p>${esc(t("lab.models_used", { requested: current.requested_model || t("lab.unrecorded"), actual: current.actual_model || t("lab.not_returned") }))}</p></div></details><details><summary>${esc(t("lab.records"))}</summary><div class="evidence-body links"><a href="${url(current.root + "ledger.jsonl")}" target="_blank" rel="noopener">${esc(t("cases.ev.ledger"))} ↗</a><a href="${url(current.root + verification)}" target="_blank" rel="noopener">${esc(t("cases.ev.verification"))} ↗</a><a href="${url(current.root + "report.html")}" target="_blank" rel="noopener">${esc(t("cases.ev.report"))} ↗</a><button class="inline-link" data-doc="${esc(guide("examples/" + current.template))}">${esc(t("lab.case_readme"))} ↗</button><span class="mono">RUN / ${esc(current.run_id)}</span></div></details></div>`;
}
function chart() {
  const scored = current.rounds.filter(r => r.score != null);
  const max = Math.max(...scored.map(r => r.score)) * 1.16;
  const points = scored.map(row => ({ row, x: 6 + 88 * row.round / Math.max(1, current.rounds.length - 1), y: 12 + 136 * (1 - row.score / max) }));
  return `<div class="panel chart-card"><div class="panel-title">${esc(t("lab.chart", { metric: current.metric }))}<span>${esc(t("lab.chart_hint"))}</span></div><div class="chart"><svg viewBox="0 0 1000 170" preserveAspectRatio="none" aria-hidden="true">${[40, 90, 148].map(y => `<line class="grid" x1="40" x2="960" y1="${y}" y2="${y}"/>`).join("")}<polyline points="${points.map(p => `${p.x * 10},${p.y}`).join(" ")}"/></svg>${points.map(p => `<button class="chart-point ${stateClass(p.row.status)} ${selected === p.row.round ? "active" : ""}" style="left:${p.x}%;top:${p.y / 170 * 100}%" data-round="${p.row.round}" aria-label="${esc(roundName(p.row.round) + " · " + number(p.row.score) + current.unit)}"></button><span class="chart-value" style="left:${p.x}%;top:${p.y / 170 * 100}%">${number(p.row.score)}${esc(unitText(current.unit))}</span>`).join("")}</div><div class="chart-labels">${current.rounds.map(r => `<span>${esc(roundName(r.round))}</span>`).join("")}</div></div>`;
}
function highlight(text) {
  const re = /(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:def|return|for|if|elif|else|in|import|from|class|None|True|False|while|try|except|raise|and|or|not|with|as|lambda|yield)\b)/g;
  let result = "", last = 0;
  for (const match of text.matchAll(re)) {
    result += esc(text.slice(last, match.index));
    const kind = match[0].startsWith("#") ? "comment" : /^['"]/.test(match[0]) ? "string" : "keyword";
    result += `<span class="syntax-${kind}">${esc(match[0])}</span>`; last = match.index + match[0].length;
  }
  return result + esc(text.slice(last));
}
function codePane(row, label) {
  const lines = row.code.split("\n");
  return `<div class="code-pane"><div class="code-pane-head"><span>${esc(label)}</span><span class="mono">${esc(row.filename)}</span></div><div class="code-content" tabindex="0" aria-label="${esc(label)}">${lines.map((line, i) => `<div class="code-line"><span class="line-number">${i + 1}</span><code>${highlight(line)}</code></div>`).join("")}</div><div class="code-pane-foot"><span>${esc(t("lab.lines", { n: lines.length }))}</span><a href="${url(row.files_base + row.filename)}" download>${esc(t("lab.download_version"))} ↓</a></div></div>`;
}
function lineDiff(left, right) {
  const a = left.split("\n"), b = right.split("\n");
  if (a.length * b.length > 1500000) return [{ type: "info", text: t("lab.diff_long") }];
  const table = Array.from({ length: a.length + 1 }, () => new Uint32Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) table[i][j] = a[i] === b[j] ? table[i + 1][j + 1] + 1 : Math.max(table[i + 1][j], table[i][j + 1]);
  const lines = []; let i = 0, j = 0;
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && a[i] === b[j]) { lines.push({ type: "", text: "  " + a[i++] }); j++; }
    else if (j < b.length && (i === a.length || table[i][j + 1] >= table[i + 1][j])) lines.push({ type: "add", text: "+ " + b[j++] });
    else lines.push({ type: "remove", text: "− " + a[i++] });
  }
  return lines;
}
function renderCode() {
  const row = current.rounds[selected], original = current.rounds[0];
  const left = state.compare === "previous" ? current.rounds[row.previous_best] : original;
  const repair = current.template === "code-repair";
  const metric = repair ? `${row.tests.passed ?? 6}<small>/ 15</small>` : `${number(row.score)}<small>×</small>`;
  const pane = state.mode === "split"
    ? `<div class="code-comparison">${codePane(left, left.round ? t("lab.code.kept_version", { n: left.round }) : t("baseline"))}${codePane(row, selected ? t("lab.code.candidate", { n: selected }) : t("baseline"))}</div>`
    : `<div class="code-pane"><div class="code-pane-head"><span>${esc(t("lab.code.diff_legend"))}</span><span class="mono">${esc(row.filename)}</span></div><div class="code-content" tabindex="0">${lineDiff(left.code, row.code).map((l, i) => `<div class="code-line ${l.type ? "diff-" + l.type : ""}"><span class="line-number">${i + 1}</span><code>${esc(l.text)}</code></div>`).join("")}</div></div>`;
  $("#lab-app").innerHTML = `<div class="lab-overview"><div class="panel result-card"><p class="eyebrow">${esc(t(repair ? "lab.code.metric_repair" : "lab.code.metric_speed"))}</p><div class="big-result">${metric}</div><p>${esc(selected ? t("lab.result_round", { n: selected }) : t("lab.result_baseline"))}</p><div class="result-subline"><span>${esc(t(repair ? "lab.code.start_repair" : "lab.code.start_speed"))}</span><strong>${esc(t(repair ? "lab.code.check_repair" : "lab.code.check_speed"))}</strong></div></div>${chart()}</div>${roundNav()}${note(row)}<div class="comparison-toolbar"><h2>${esc(t("lab.code.compare"))}</h2><div class="control-group"><div class="select-wrap"><select id="comparison-base" aria-label="${esc(t("lab.code.compare_base"))}"><option value="baseline" ${state.compare === "baseline" ? "selected" : ""}>${esc(t("lab.code.vs_baseline"))}</option><option value="previous" ${state.compare === "previous" ? "selected" : ""}>${esc(t("lab.code.vs_previous"))}</option></select></div><div class="segmented" role="group"><button data-mode="split" class="${state.mode === "split" ? "active" : ""}">${esc(t("lab.code.split"))}</button><button data-mode="diff" class="${state.mode === "diff" ? "active" : ""}">${esc(t("lab.code.diff"))}</button></div></div></div>${pane}<p class="source-note">${esc(t(repair ? "lab.code.source_repair" : "lab.code.source_speed"))}</p>${actions()}${evidence()}`;
  $("#comparison-base").addEventListener("change", e => { state.compare = e.target.value; syncAddress(); render(); });
  $$("[data-mode]").forEach(b => b.addEventListener("click", () => { state.mode = b.dataset.mode; syncAddress(); render(); }));
  const panes = $$(".code-content");
  if (panes.length === 2) {
    let syncing = false;
    panes.forEach((p, i) => p.addEventListener("scroll", () => {
      if (syncing) return;
      syncing = true; panes[1 - i].scrollTop = p.scrollTop;
      requestAnimationFrame(() => { syncing = false; });
    }));
  }
}
function imageCard(path, title, subtitle) {
  return `<div class="panel image-card"><div class="panel-title">${esc(title)}<span>${esc(subtitle)}</span></div><button data-image="${url(path)}" data-title="${esc(title)}" aria-label="${esc(t("lab.zoom") + " · " + title)}"><img src="${url(path)}" alt="${esc(title)}" loading="lazy"></button><div class="image-card-foot">${esc(t("lab.image_foot"))}</div></div>`;
}
function renderModel() {
  const row = current.rounds[selected], original = current.rounds[0], displayed = row.formal ? row : current.rounds[row.previous_best];
  const metrics = displayed.metrics, first = original.metrics, configuration = displayed.configuration;
  let matrix = "<span></span>" + Array.from({ length: 10 }, (_, i) => `<span>${i}</span>`).join("");
  const peak = Math.max(...metrics.confusion_matrix.flat());
  metrics.confusion_matrix.forEach((line, real) => {
    matrix += `<span>${real}</span>`;
    line.forEach((value, predicted) => {
      const kind = !value ? "" : real === predicted ? "hit" : "miss";
      matrix += `<button class="${kind}" style="--a:${value ? 0.2 + 0.8 * Math.min(1, value / peak) : 0}" data-cell="${real},${predicted}" aria-label="${esc(t("lab.model.cell", { real, predicted, n: value }))}">${value || "·"}</button>`;
    });
  });
  const keys = ["model", "scaling", "pca_components"];
  const configRows = keys.map(k => `<tr><td>${esc(t("lab.model.param." + k))}</td><td>${esc(original.configuration[k])}</td><td>${esc(configuration[k])}</td></tr>`).join("") + `<tr><td>${esc(t("lab.model.param.params"))}</td><td class="mono">${esc(JSON.stringify(original.configuration.params))}</td><td class="mono">${esc(JSON.stringify(configuration.params))}</td></tr>`;
  $("#lab-app").innerHTML = `<div class="lab-overview"><div class="panel result-card"><p class="eyebrow">${esc(t("lab.model.metric"))}</p><div class="big-result">${number(metrics.accuracy_percent)}<small>%</small></div><p>${esc(displayed.round ? t("lab.model.round_model", { n: displayed.round }) : t("lab.model.baseline_model"))}</p><div class="result-subline"><span>${esc(t("lab.model.samples"))} <strong>450</strong></span><span>${esc(t("lab.model.misread"))} <strong>${metrics.mistakes}</strong></span><span>CPU</span></div></div><div class="panel accuracy-lines"><div class="panel-title">${esc(t("lab.model.progress"))}<span>${esc(t("lab.model.higher"))}</span></div>${[[first.accuracy_percent, t("lab.model.acc_baseline")], [metrics.accuracy_percent, t("lab.model.acc_current")]].map(([value, label], i) => `<div class="accuracy-row"><div><span>${esc(label)}</span><span class="mono">${number(value)}%</span></div><div class="accuracy-track ${i ? "now" : ""}"><i style="width:${value}%"></i></div></div>`).join("")}<p>${esc(t("lab.model.summary"))}</p></div></div>${roundNav()}${note(row)}<div class="model-grid"><div class="panel matrix-card"><div class="panel-title">${esc(t("lab.model.matrix"))}<span>${esc(t("lab.model.matrix_hint"))}</span></div><div class="matrix-wrap"><div class="matrix-axis">${esc(t("lab.model.true_digit"))}</div><div class="matrix" role="group" aria-label="${esc(t("lab.model.matrix"))}">${matrix}</div></div><div class="matrix-caption">${esc(t("lab.model.predicted_digit"))}</div><p class="subtle">${esc(t("lab.model.matrix_note"))}</p></div><div class="panel config-card"><div class="panel-title">${esc(t("lab.model.config"))}<span>${esc(t("lab.model.config_cols"))}</span></div><div class="table-scroll"><table class="config-table"><thead><tr><th>${esc(t("lab.model.param.name"))}</th><th>${esc(t("baseline"))}</th><th>${esc(t("lab.model.current"))}</th></tr></thead><tbody>${configRows}</tbody></table></div><p class="subtle">${esc(t("lab.model.config_note"))}</p><p class="subtle">${esc(t("lab.model.timing", { s: number(metrics.train_predict_seconds) }))}</p></div></div><div class="panel prediction-card"><div class="panel-title">${esc(t("lab.model.predictions"))}<span>${esc(t("lab.model.predictions_hint"))}</span></div><div class="prediction-toolbar"><div><label class="check"><input id="only-errors" type="checkbox" checked> ${esc(t("lab.model.only_errors"))}</label><div class="select-wrap small"><select id="digit-filter" aria-label="${esc(t("lab.model.filter_digit"))}"><option value="">${esc(t("lab.model.all_digits"))}</option>${Array.from({ length: 10 }, (_, i) => `<option>${i}</option>`).join("")}</select></div><button class="inline-link" id="clear-filter">${esc(t("lab.model.reset"))}</button></div><span id="prediction-count" class="mono"></span></div><div id="prediction-table" class="predictions-table"></div></div><div class="comparison-toolbar"><h2>${esc(t("lab.model.images"))}</h2><span class="subtle">${esc(t("lab.model.images_hint"))}</span></div><div class="image-comparison">${imageCard(original.files_base + "out/mistakes.png", t("lab.model.mistakes_baseline"), t("lab.model.first12"))}${imageCard(displayed.files_base + "out/mistakes.png", t("lab.model.mistakes_current"), t("lab.model.n_misread", { n: metrics.mistakes }))}</div>${actions()}${evidence()}`;
  let pair = null;
  function filterPredictions() {
    const only = $("#only-errors").checked, digit = $("#digit-filter").value;
    const matches = displayed.predictions.filter(p => (!only || !p.correct) && (digit === "" || p.expected === Number(digit)) && (!pair || p.expected === pair[0] && p.predicted === pair[1]));
    $("#prediction-count").textContent = `${pair ? t("lab.model.pair", { a: pair[0], b: pair[1] }) + " · " : ""}${t("lab.model.count", { n: matches.length })}${matches.length > 80 ? " · " + t("lab.model.first80") : ""}`;
    $("#prediction-table").innerHTML = matches.length ? `<table><thead><tr><th>${esc(t("lab.model.col_sample"))}</th><th>${esc(t("lab.model.col_true"))}</th><th>${esc(t("lab.model.col_pred"))}</th><th>${esc(t("lab.model.col_result"))}</th></tr></thead><tbody>${matches.slice(0, 80).map(p => `<tr><td class="mono">${p.sample_id}</td><td>${p.expected}</td><td>${p.predicted}</td><td><span class="pill ${p.correct ? "keep" : "revert"}">${esc(t(p.correct ? "lab.model.correct" : "lab.model.wrong"))}</span></td></tr>`).join("")}</tbody></table>` : `<div class="table-empty">${esc(t("lab.model.empty"))}</div>`;
  }
  const clearCells = () => $$("[data-cell]").forEach(b => b.classList.remove("selected"));
  $("#only-errors").addEventListener("change", filterPredictions);
  $("#digit-filter").addEventListener("change", () => { pair = null; clearCells(); filterPredictions(); });
  $("#clear-filter").addEventListener("click", () => { pair = null; $("#only-errors").checked = true; $("#digit-filter").value = ""; clearCells(); filterPredictions(); });
  $$("[data-cell]").forEach(b => b.addEventListener("click", () => { pair = b.dataset.cell.split(",").map(Number); $("#digit-filter").value = ""; $("#only-errors").checked = false; $$("[data-cell]").forEach(x => x.classList.toggle("selected", x === b)); filterPredictions(); }));
  filterPredictions();
}
function renderVideo() {
  const row = current.rounds[selected];
  const special = row.status === "REVERT" && row.score > current.rounds[row.previous_best].score;
  const heading = selected === current.best_round ? t("lab.video.h_kept") : special ? t("lab.video.h_special") : selected ? t("lab.video.h_try") : t("lab.video.h_base");
  const noteTitle = special ? t("lab.video.n_special") : selected === current.best_round ? t("lab.video.n_kept", { n: selected }) : selected ? t("lab.video.n_try") : t("lab.video.n_base");
  const noteBody = special ? t("lab.video.special_body", { score: number(row.score), best: number(current.rounds[row.previous_best].score) }) : (row.note || t("lab.video.base_body"));
  $("#lab-app").innerHTML = `${roundNav()}<div class="cinema"><div class="cinema-top"><span class="mono">${selected ? "ROUND " + String(selected).padStart(2, "0") : "BASELINE"} / ${esc(t("lab.video.source_short"))}</span>${pill(row)}</div><div class="cinema-body"><div class="player-stage"><div class="phone"><video id="cut-player" controls playsinline preload="metadata" poster="${selected === current.best_round ? url("assets/video-poster.jpg") : ""}" src="${url(row.files_base + "out/cut.mp4")}"><track kind="captions" src="${url(row.files_base + "out/cut.vtt")}" srclang="en" label="English"></video></div></div><div class="cinema-info"><p class="eyebrow">${esc(selected === current.best_round ? t("lab.video.e_kept") : t("lab.video.e_cut"))}</p><h2>${esc(heading)}</h2><p>${esc(t("lab.video.summary." + selected))}</p><div class="video-stats"><div><span>${esc(t("lab.video.duration"))}</span><strong>${row.duration.toFixed(1)}<small>${esc(t("unit.s"))}</small></strong></div><div><span>${esc(t("lab.video.score"))}</span><strong>${number(row.score)}<small>${esc(current.unit)}</small></strong></div><div><span>${esc(t("lab.video.segments"))}</span><strong>${row.segments.length}</strong></div></div><div class="cue-heading">${esc(t("lab.video.transcript"))}<span>${esc(t("lab.video.transcript_hint"))}</span></div><div class="cue-list" aria-label="${esc(t("lab.video.transcript"))}">${row.cues.map((cue, i) => `<button class="cue" data-cue="${i}"><time>${clock(cue.start)}</time><span>${esc(cue.text)}</span></button>`).join("")}</div></div></div></div><div class="callout ${row.status === "REVERT" ? "warning" : ""}"><strong>${esc(noteTitle)}</strong><p>${esc(noteBody)}</p><p>${esc(t("lab.video.caveat"))}</p></div><div class="video-context"><div class="panel"><h3>${esc(t("lab.video.which"))}</h3><p>${esc(t("lab.video.which_body"))}</p><div class="segment-map">${row.segments.map(id => `<span>${id}</span>`).join("")}</div><a class="inline-link" href="${url(row.files_base + "edit.json")}" target="_blank" rel="noopener">${esc(t("lab.video.plan"))} ↗</a></div><details class="panel" id="original-video"><summary>${esc(t("lab.video.original"))}</summary><p>${esc(t("lab.video.original_body"))}</p><video controls playsinline preload="none" src="${url("examples/video-cut/inputs/public-speech/input.mp4")}"></video><p class="subtle">${esc(t("lab.video.compare_hint"))}</p></details></div><div class="lab-actions"><a class="btn btn-primary" href="${url(row.files_base + "out/cut.mp4")}" download>${esc(t("lab.video.dl_cut"))}<span aria-hidden="true">↓</span></a><a class="btn btn-ghost" href="${url(row.files_base + "out/cut.srt")}" download>${esc(t("lab.video.dl_srt"))}<span aria-hidden="true">↓</span></a><button class="btn btn-ghost" id="share-run">${esc(t("lab.copy_link"))}</button><a class="btn btn-ghost" href="${url("downloads/video-cut.zip")}" download>${esc(t("lab.download_all"))}<span aria-hidden="true">↓</span></a></div>${evidence()}`;
  const video = $("#cut-player");
  $$("[data-cue]").forEach(b => b.addEventListener("click", () => {
    video.currentTime = row.cues[Number(b.dataset.cue)].start;
    video.play().catch(() => toast(t("lab.video.press_play")));
  }));
  video.addEventListener("timeupdate", () => {
    const time = video.currentTime;
    $$("[data-cue]").forEach(b => { const cue = row.cues[Number(b.dataset.cue)]; b.classList.toggle("active", time >= cue.start && time < cue.end); });
  });
  $("#original-video").addEventListener("toggle", e => { if (!e.target.open) $("video", e.target).pause(); });
}
/* ---------- visual lab ---------- */
let playTimer = null;
function stopPlay() { clearInterval(playTimer); playTimer = null; }
const visualLabel = row => (current.runs.length > 1 ? t("lab.visual.run", { n: row.run + 1 }) + " · " : "") + roundName(row.number);
function visualFigure(row, image, caption, extra = "") {
  const src = url(row.files_base + image);
  return `<figure class="vis-frame ${extra}"><button data-image="${src}" data-title="${esc(caption)}" aria-label="${esc(t("lab.zoom") + " · " + caption)}"><img src="${src}" alt="${esc(caption)}"></button><figcaption>${esc(caption)}</figcaption></figure>`;
}
function visualStage(row, then) {
  if (current.template === "svg-drawing") {
    const image = row.images[0];
    return `<div class="vis-compare ${then ? "two" : ""}">${then ? visualFigure(then, image, t("lab.visual.best_then") + " · " + visualLabel(then), "then") : ""}${visualFigure(row, image, (row.number ? t("lab.visual.this_round") : t("lab.visual.start_label")) + " · " + visualLabel(row), "now")}</div>`;
  }
  const shown = state.view === "then" && then ? then : row;
  const which = shown === row ? (row.number ? t("lab.visual.this_round") : t("lab.visual.start_label")) : t("lab.visual.best_then");
  const toggle = then ? `<div class="segmented vis-toggle" role="group" aria-label="${esc(t("lab.visual.compare"))}"><button data-view="now" class="${shown === row ? "active" : ""}" aria-pressed="${shown === row}">${esc(t("lab.visual.this_round"))}</button><button data-view="then" class="${shown === row ? "" : "active"}" aria-pressed="${shown !== row}">${esc(t("lab.visual.best_then"))}</button></div>` : "";
  const shot = (image, label, kind) => `<figure class="vis-shot ${kind}"><button data-image="${url(shown.files_base + image)}" data-title="${esc(which + " · " + label)}" aria-label="${esc(t("lab.zoom") + " · " + label)}"><img src="${url(shown.files_base + image)}" alt="${esc(which + " · " + label)}"></button><figcaption>${esc(label)}</figcaption></figure>`;
  return `<div class="vis-page-head"><span>${esc(which + " · " + visualLabel(shown))}</span>${toggle}</div><div class="vis-page">${shot("out/desktop.png", t("lab.visual.desktop"), "desktop")}${shot("out/mobile.png", t("lab.visual.phone"), "mobile")}</div>`;
}
function renderVisual() {
  const row = current.rounds[selected], run = current.runs[row.run];
  const then = row.number ? current.rounds[row.previous_best] : null;
  const delta = row.score != null && row.best_before != null && row.number ? row.score - row.best_before : null;
  const heading = !row.number ? t(row.run ? "lab.visual.h_run" : "lab.visual.h_base", { n: row.run + 1 })
    : selected === current.best_round ? t("lab.visual.h_final")
    : row.status === "KEEP" ? t(delta === 0 ? "lab.visual.h_tie_kept" : "lab.visual.h_kept")
    : row.status === "REVERT" ? t(delta > 0 ? "lab.visual.h_lost" : delta < 0 ? "lab.visual.h_rejected" : run.ties ? "lab.visual.h_tie_lost" : "lab.visual.h_same")
    : t("lab.visual.h_other");
  const kept = current.rounds.filter(r => r.round <= row.round && r.number && r.status === "KEEP").length;
  const deltaText = delta == null ? "—" : (delta > 0 ? "+" : delta < 0 ? "−" : "±") + number(Math.abs(delta));
  const criteria = current.criteria.map(c => {
    const value = row.criteria[c.name], before = then?.criteria[c.name];
    return `<div class="crit"><div class="crit-head"><span>${esc(t("lab.visual.criteria." + c.name))}<small>${c.weight}%</small></span><span class="mono">${value == null ? "—" : number(value)}<small>/10</small></span></div><div class="crit-track"><i style="width:${(value || 0) * 10}%"></i>${before == null ? "" : `<b style="left:${before * 10}%"></b>`}</div></div>`;
  }).join("");
  const film = current.rounds.map(r => `${r.number === 0 && r.run ? `<div class="film-run"><strong>${esc(t("lab.visual.run", { n: r.run + 1 }))}</strong><span>${esc(current.runs[r.run].ties ? t("lab.visual.rule_ties") : t("lab.visual.rule_same"))}</span></div>` : ""}<button class="film-item ${stateClass(r.status)} ${selected === r.round ? "active" : ""}" data-round="${r.round}" aria-pressed="${selected === r.round}" aria-label="${esc(visualLabel(r) + " · " + status(r.status) + " · " + number(r.score))}"><span class="film-thumb"><img src="${url(r.files_base + r.images[0])}" alt="" loading="lazy"></span><span class="film-meta"><span>R${r.number}</span><strong>${number(r.score)}</strong></span>${pill(r)}</button>`).join("");
  const story = current.template === "svg-drawing" ? "story_pelican" : "story_landing";
  $("#lab-app").innerHTML = `<div class="cinema vis-cinema"><div class="cinema-top"><span class="mono">${esc(visualLabel(row).toUpperCase())}</span>${pill(row)}</div><div class="vis-body"><div class="vis-stage">${visualStage(row, then)}</div><div class="cinema-info"><p class="eyebrow">${esc(current.title)}</p><h2>${esc(heading)}</h2><p>${esc(row.hypothesis || (row.run ? t("lab.visual.run_body", { n: row.run + 1 }) : t("lab.visual.base_body")))}</p><div class="video-stats"><div><span>${esc(t("lab.visual.score"))}</span><strong class="${row.status === "REVERT" ? "flat" : ""}">${number(row.score)}<small>${esc(current.unit)}</small></strong></div><div><span>${esc(t("lab.visual.vs_best"))}</span><strong class="${delta > 0 ? "" : "flat"}">${deltaText}</strong></div><div><span>${esc(t("lab.visual.kept"))}</span><strong>${kept}</strong></div></div><div class="crit-list" aria-label="${esc(t("lab.visual.criteria_label"))}">${criteria}</div><p class="crit-legend">${esc(t(then ? "lab.visual.legend" : "lab.visual.legend_single"))}</p></div></div></div>
    <div class="callout ${row.status === "REVERT" ? "warning" : ""}"><strong>${esc(t("lab.visual.decision"))}</strong><p>${esc(row.note || t(row.run ? "lab.visual.run_note" : "lab.visual.base_note"))}</p></div>
    <div class="round-header vis-film-head"><h2>${esc(t("lab.visual.film"))}</h2><span>${esc(t("lab.visual.film_hint"))}</span><button class="btn btn-soft vis-play" id="vis-play" aria-pressed="${Boolean(playTimer)}">${playTimer ? `<span class="pause" aria-hidden="true"></span>${esc(t("lab.visual.pause"))}` : `<span class="play" aria-hidden="true"></span>${esc(t("lab.visual.play"))}`}</button></div>
    <div class="film" role="group" aria-label="${esc(t("lab.visual.film"))}">${film}</div>
    <div class="callout story-callout"><strong>${esc(t("lab.visual." + story + "_title"))}</strong><p>${esc(t("lab.visual." + story))}</p></div>
    <details class="panel vis-feedback"><summary>${esc(t("lab.visual.feedback"))}<span>${esc(t("lab.visual.feedback_hint"))}</span></summary><pre>${esc(row.feedback)}</pre></details>
    <div class="lab-actions"><a class="btn btn-primary" href="${url(row.files_base + row.source)}" download>${esc(t("lab.visual.dl_source", { name: row.source }))}<span aria-hidden="true">↓</span></a><a class="btn btn-ghost" href="${url("examples/" + current.template + "/evolution.html")}" target="_blank" rel="noopener">${esc(t("lab.visual.open_page"))}<span aria-hidden="true">↗</span></a><button class="btn btn-ghost" id="share-run">${esc(t("lab.copy_link"))}</button><a class="btn btn-ghost" href="${url("downloads/" + current.template + ".zip")}" download>${esc(t("lab.download_all"))}<span aria-hidden="true">↓</span></a></div>
    <div class="evidence-section"><details><summary>${esc(t("lab.scope"))}</summary><div class="evidence-body"><p>${esc(t("lab.limits." + current.template))}</p><p>${esc(t("lab.visual.models", { agent: current.requested_model || t("lab.unrecorded"), jury: current.jury.join(", ") }))}</p></div></details><details><summary>${esc(t("lab.records"))}</summary><div class="evidence-body links">${current.runs.map((r, i) => `<span class="mono">${esc(current.runs.length > 1 ? t("lab.visual.run", { n: i + 1 }) + " / " : "RUN / ")}${esc(r.id)}</span><a href="${url(r.root + "ledger.jsonl")}" target="_blank" rel="noopener">${esc(t("cases.ev.ledger"))} ↗</a><a href="${url(r.root + "verification.json")}" target="_blank" rel="noopener">${esc(t("cases.ev.verification"))} ↗</a><a href="${url(r.root + "report.html")}" target="_blank" rel="noopener">${esc(t("cases.ev.report"))} ↗</a>`).join("")}<button class="inline-link" data-doc="${esc(guide("examples/" + current.template))}">${esc(t("lab.case_readme"))} ↗</button></div></details></div>`;
  $$("[data-view]").forEach(b => b.addEventListener("click", () => { state.view = b.dataset.view; render(); }));
  $$(".film-item").forEach(b => b.addEventListener("click", () => { stopPlay(); state.view = "now"; }));
  $("#vis-play").addEventListener("click", () => {
    if (playTimer) { stopPlay(); render(); return; }
    const path = current.rounds.filter(r => (r.number === 0 && r.run === 0) || r.status === "KEEP").map(r => r.round);
    let step = 0;
    const show = () => { selected = path[step]; state.view = "now"; syncAddress(); render(); };
    playTimer = setInterval(() => { step += 1; if (step >= path.length - 1) stopPlay(); show(); }, reduceMotion ? 2400 : 1600);
    show();
  });
}
function render() {
  if (page === "code") renderCode();
  if (page === "experiments") renderModel();
  if (page === "video") renderVideo();
  if (page === "visual") renderVisual();
  const strip = $(".round-nav") || $(".film"), active = $(".round-button.active") || $(".film-item.active");
  if (strip && active && strip.scrollWidth > strip.clientWidth) strip.scrollLeft += active.getBoundingClientRect().left - strip.getBoundingClientRect().left - (strip.clientWidth - active.clientWidth) / 2;
  $$("[data-round]").forEach(b => b.addEventListener("click", () => { selected = Number(b.dataset.round); syncAddress(); render(); }));
  $("#share-run")?.addEventListener("click", () => copy(location.href));
}
async function loadCase(fromUrl = false) {
  const id = ++loadId;
  $$("[data-case]").forEach(b => { b.classList.toggle("active", b.dataset.case === state.template); b.setAttribute("aria-pressed", String(b.dataset.case === state.template)); });
  try {
    const response = await fetch(url(`data/${lang}/${state.template}.json`));
    if (!response.ok) throw new Error("missing");
    const data = await response.json();
    if (id !== loadId) return;
    current = data;
    const query = new URLSearchParams(location.search), round = Number(query.get("round"));
    selected = fromUrl && query.has("round") && Number.isInteger(round) && current.rounds.some(r => r.round === round) ? round : current.best_round;
    syncAddress(); render();
  } catch {
    if (id !== loadId) return;
    $("#lab-app").innerHTML = `<div class="load-error"><h2>${esc(t("load_error"))}</h2><p>${esc(t("load_error_body"))}</p><button class="btn btn-ghost" id="retry-load">${esc(t("retry"))}</button></div>`;
    $("#retry-load").addEventListener("click", () => loadCase(true));
  }
}

/* ---------- all experiments ---------- */
async function renderCases() {
  const list = $("#case-list"), detail = $("#case-detail"), filters = $("#case-filters");
  let data;
  try {
    const response = await fetch(url(`data/${lang}/cases.json`));
    if (!response.ok) throw new Error("missing");
    data = await response.json();
  } catch {
    detail.innerHTML = `<div class="load-error"><h2>${esc(t("load_error"))}</h2><p>${esc(t("load_error_body"))}</p></div>`;
    return;
  }
  const categories = [...new Set(data.domains.map(d => d.category))];
  const filterKeys = ["all", "complete", "partial", ...categories];
  let filter = "all", domainId = data.domains.some(d => d.id === location.hash.slice(1)) ? location.hash.slice(1) : "D01";
  let caseIndex = 0, runIndex = 0, mode = "split", picks = [[0, 0], [0, 0]];
  const textCache = new Map();
  const stateLabel = d => d.state === "complete" ? t("cases.state.complete") : (d.exception_label || t("cases.state." + d.state));
  const stateTone = d => d.state === "complete" ? "keep" : d.state === "resource_exception" ? "warn" : "";
  const result = (run, domain) => run && run.best != null ? `${number(run.baseline)} → ${number(run.best)}${esc(unitText(domain.unit))}` : "—";
  const matches = d => filter === "all" || (filter === "complete" ? d.state === "complete" : filter === "partial" ? d.state !== "complete" : d.category === filter);
  const chosen = () => { const domain = data.domains.find(d => d.id === domainId); const example = domain.cases[caseIndex] || domain.cases[0]; return { domain, example, run: example.runs[runIndex] }; };
  const versionLabel = v => v.kind === "baseline" ? t("cases.v_baseline") : v.kind === "final" ? t("cases.v_final") : `${roundName(v.round)} · ${v.quality_unknown ? t("status.unknown") : status(v.status)}`;

  function renderFilters() {
    filters.innerHTML = filterKeys.map(key => `<button class="chip ${filter === key ? "active" : ""}" data-filter="${esc(key)}" aria-pressed="${filter === key}">${esc(["all", "complete", "partial"].includes(key) ? t("cases.filter_" + key) : key)}</button>`).join("");
    $$("[data-filter]", filters).forEach(b => b.addEventListener("click", () => { filter = b.dataset.filter; renderFilters(); renderList(); }));
  }
  function renderList() {
    list.innerHTML = data.domains.filter(matches).map(d => {
      const head = d.cases[0], run = head.runs[head.preferred_run];
      return `<button class="case-item ${d.id === domainId ? "active" : ""}" data-domain="${d.id}" aria-current="${d.id === domainId}"><span class="case-id mono">${d.id}</span><span class="case-main"><strong>${esc(d.title)}</strong><small>${esc(d.category)} · ${result(run, d)}</small></span><span class="dot ${stateTone(d)}" title="${esc(stateLabel(d))}"></span></button>`;
    }).join("") || `<p class="subtle">${esc(t("cases.none"))}</p>`;
    $$("[data-domain]", list).forEach(b => b.addEventListener("click", () => selectDomain(b.dataset.domain, true)));
  }
  function selectDomain(id, scroll = false) {
    domainId = id; caseIndex = 0; runIndex = chosen().example.preferred_run || 0; mode = "split";
    history.replaceState(null, "", "#" + id);
    renderList(); renderDetail();
    if (scroll && matchMedia("(max-width: 900px)").matches) detail.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  }
  function link(item, label) { return `<a href="${esc(url(item.url))}" target="_blank" rel="noopener">${esc(label || item.name)} ↗</a>`; }
  function modelText(run) {
    const parts = [t("cases.m_agent", { v: run.agent || t("lab.unrecorded") }), t("cases.m_requested", { v: run.requested_model || t("lab.unrecorded") }), t("cases.m_actual", { v: run.actual_model || t("lab.not_returned") })];
    if (run.reasoning_effort) parts.push(t("cases.m_effort", { v: run.reasoning_effort }));
    parts.push(run.jury?.length ? t("cases.m_jury", { v: run.jury.join(", ") }) : t("cases.m_program"));
    if (run.task_model) parts.push(t("cases.m_task", { v: run.task_model }));
    return parts.join(" · ");
  }
  function renderDetail() {
    const { domain, example, run } = chosen();
    let html = `<header class="case-head"><p class="eyebrow">${domain.id} · ${esc(domain.category)} <span class="pill ${stateTone(domain)}">${esc(stateLabel(domain))}</span></p><h2>${esc(domain.title)}</h2><p class="lede">${esc(domain.description)}</p>${domain.note ? `<div class="callout">${esc(domain.note)}</div>` : ""}${domain.cases.length > 1 ? `<div class="segmented case-tabs" role="group">${domain.cases.map((c, i) => `<button data-case-tab="${i}" class="${i === caseIndex ? "active" : ""}">${esc(c.title)}</button>`).join("")}</div>` : ""}</header>`;
    if (!run) {
      html += `<div class="empty-state"><strong>${esc(stateLabel(domain))}</strong><p>${esc(t("cases.no_runs"))}</p><div class="links">${[example.template_readme && link(example.template_readme, t("cases.template_readme")), example.readme && link(example.readme, t("cases.case_readme")), domain.probe && link(domain.probe, t("cases.probe"))].filter(Boolean).join("")}</div></div>`;
      detail.innerHTML = html; bindTabs(); return;
    }
    if (example.runs.length > 1) html += `<div class="run-picker"><label for="run-select" class="field-label">${esc(t("cases.run"))}</label><div class="select-wrap"><select id="run-select">${example.runs.map((r, i) => `<option value="${i}" ${i === runIndex ? "selected" : ""}>${esc(r.id)} · ${esc(r.eligible ? t("cases.run_complete") : r.invalid_reason ? t("cases.run_invalid") : r.finished ? t("cases.run_partial") : t("cases.run_unfinished"))}</option>`).join("")}</select></div></div>`;
    if (run.reasons.length) html += `<div class="callout warning">${run.reasons.map(r => `<p>${esc(r)}</p>`).join("")}</div>`;
    html += `<div class="stats"><div><span>${esc(t("cases.s_baseline", { metric: domain.metric }))}</span><strong>${number(run.baseline)}<small>${run.baseline == null ? "" : esc(domain.unit)}</small></strong></div><div><span>${esc(t("cases.s_best"))}</span><strong>${number(run.best)}<small>${run.best == null ? "" : esc(domain.unit)}</small></strong></div><div><span>${esc(t("cases.s_attempts"))}</span><strong>${run.rounds}</strong></div><div><span>${esc(t("cases.s_kept"))}</span><strong>${run.kept}<small>/ ${run.rounds}</small></strong></div></div>`;
    if (run.quality_unknown_rounds.length) html += `<div class="callout warning">${esc(t("cases.unknown_rounds", { list: run.quality_unknown_rounds.join(", ") }))}</div>`;
    if (run.holdout && run.holdout.final != null) html += `<div class="callout">${esc(t("cases.holdout", { a: number(run.holdout.baseline), b: number(run.holdout.final) }))}</div>`;
    html += `<h3 class="block-title">${esc(t("cases.rounds"))}</h3><ol class="timeline">${run.rows.map(r => `<li class="${stateClass(r.status)}"><div class="tl-head"><span class="tl-round mono">${r.round ? "R" + r.round : "R0"}</span><span class="pill ${stateClass(r.quality_unknown ? "JUDGE_FAIL" : r.status)}">${esc(r.quality_unknown ? t("status.unknown") : status(r.status))}</span><span class="tl-score">${number(r.score)}${r.score == null ? "" : esc(unitText(domain.unit))}</span></div>${r.hypothesis ? `<p>${esc(r.hypothesis)}</p>` : ""}${r.note ? `<p class="tl-note">${esc(r.note)}</p>` : ""}${r.feedback ? `<details><summary>${esc(t("cases.feedback"))}</summary><p class="feedback">${esc(r.feedback)}</p></details>` : ""}</li>`).join("")}</ol>`;
    html += `<div class="compare-toolbar"><h3 class="block-title">${esc(t("cases.versions"))}</h3><div class="segmented" role="group"><button data-view="split" class="${mode === "split" ? "active" : ""}">${esc(t("cases.split"))}</button><button data-view="diff" class="${mode === "diff" ? "active" : ""}">${esc(t("cases.diff"))}</button></div></div><p class="subtle">${esc(t("cases.original_language"))}</p><div id="version-area"></div>`;
    html += `<details class="panel fold"><summary>${esc(t("cases.inputs"))}</summary><p class="pre">${esc(run.goal)}</p><div class="links">${run.inputs.map(i => link(i, (i.original ? t("cases.original_input") + " · " : "") + i.name)).join("") || esc(t("cases.no_inputs"))}</div></details><details class="panel fold"><summary>${esc(t("cases.evidence"))}</summary><div class="links">${run.evidence.map(e => link(e, e.key ? t("cases.ev." + e.key) : e.name)).join("")}${example.readme ? link(example.readme, t("cases.case_readme")) : ""}${example.template_readme ? link(example.template_readme, t("cases.template_readme")) : ""}</div><p class="subtle">${esc(modelText(run))}</p><p class="subtle">${esc(t("cases.costs"))} ${esc(t("cases.started", { v: run.started || "—" }))} · ${esc(t("cases.stop", { v: run.stop_reason || "—" }))}</p><p class="mono subtle">RUN / ${esc(run.id)}</p></details>`;
    detail.innerHTML = html;
    bindTabs();
    $("#run-select")?.addEventListener("change", e => { runIndex = Number(e.target.value); mode = "split"; renderDetail(); });
    $$("[data-view]", detail).forEach(b => b.addEventListener("click", () => {
      mode = b.dataset.view;
      $$("[data-view]", detail).forEach(x => x.classList.toggle("active", x === b));
      if (mode === "diff") picks = picks.map(([v, f]) => {
        const files = run.versions[v]?.files || [];
        return [v, files[f]?.kind === "text" ? f : Math.max(0, files.findIndex(x => x.kind === "text"))];
      });
      renderVersions();
    }));
    picks = [[0, 0], [Math.max(0, run.versions.length - 1), 0]];
    renderVersions();
  }
  function bindTabs() { $$("[data-case-tab]", detail).forEach(b => b.addEventListener("click", () => { caseIndex = Number(b.dataset.caseTab); runIndex = chosen().example.preferred_run || 0; renderDetail(); })); }
  async function fileText(file) {
    if (!textCache.has(file.url)) textCache.set(file.url, fetch(url(file.url)).then(r => r.ok ? r.text() : Promise.reject(new Error("missing"))));
    return textCache.get(file.url);
  }
  async function renderVersions() {
    const { run } = chosen(), area = $("#version-area");
    if (!run.versions.length) { area.innerHTML = `<div class="empty-state">${esc(t("cases.no_versions"))}</div>`; return; }
    const side = s => {
      const v = run.versions[picks[s][0]];
      return `<section class="version"><div class="version-controls"><div class="select-wrap small"><select data-pick-version="${s}" aria-label="${esc(t(s ? "cases.right_version" : "cases.left_version"))}">${run.versions.map((x, i) => `<option value="${i}" ${i === picks[s][0] ? "selected" : ""}>${esc(versionLabel(x))}</option>`).join("")}</select></div><div class="select-wrap small"><select data-pick-file="${s}" aria-label="${esc(t("cases.file"))}">${v.files.map((f, i) => `<option value="${i}" ${i === picks[s][1] ? "selected" : ""}>${esc(f.name)}</option>`).join("")}</select></div></div>${v.note ? `<p class="subtle">${esc(v.note)}</p>` : ""}<div class="viewer" id="viewer-${s}"><div class="loading"><span></span></div></div><div class="viewer-foot" id="viewer-foot-${s}"></div></section>`;
    };
    area.innerHTML = `<div class="comparison ${mode}">${side(0)}${side(1)}</div><div class="text-diff" id="text-diff"></div>`;
    $$("[data-pick-version]", area).forEach(s => s.addEventListener("change", e => { picks[Number(s.dataset.pickVersion)] = [Number(e.target.value), 0]; renderVersions(); }));
    $$("[data-pick-file]", area).forEach(s => s.addEventListener("change", e => { picks[Number(s.dataset.pickFile)][1] = Number(e.target.value); renderVersions(); }));
    const files = [0, 1].map(s => run.versions[picks[s][0]]?.files[picks[s][1]]);
    if (mode === "diff") {
      const box = $("#text-diff");
      if (files.every(f => f?.kind === "text")) {
        try {
          const [a, b] = await Promise.all(files.map(fileText));
          box.innerHTML = `<div class="code-pane"><div class="code-content tall">${lineDiff(a, b).map((l, i) => `<div class="code-line ${l.type ? "diff-" + l.type : ""}"><span class="line-number">${i + 1}</span><code>${esc(l.text)}</code></div>`).join("")}</div></div>`;
        } catch { box.innerHTML = `<p class="callout warning">${esc(t("doc_failed"))}</p>`; }
      } else box.innerHTML = `<p class="callout">${esc(t("cases.diff_pick"))}</p>`;
    }
    await Promise.all([0, 1].map(s => renderFile(s, files[s])));
  }
  async function renderFile(s, file) {
    const view = $("#viewer-" + s), foot = $("#viewer-foot-" + s);
    if (!view) return;
    if (!file) { view.innerHTML = `<div class="empty-state">${esc(t("cases.no_file"))}</div>`; return; }
    foot.innerHTML = `${link(file, t("cases.open_file"))}<span class="mono">${(file.bytes / 1024).toFixed(1)} KB</span>`;
    if (file.kind === "image") view.innerHTML = `<button class="zoom" data-image="${esc(url(file.url))}" data-title="${esc(file.name)}"><img src="${esc(url(file.url))}" alt="${esc(file.name)}" loading="lazy"></button>`;
    else if (file.kind === "video") view.innerHTML = `<video controls playsinline preload="metadata" src="${esc(url(file.url))}"></video>`;
    else if (file.kind === "html" || file.kind === "text") {
      try {
        let text = await fileText(file);
        if (file.kind === "html") {
          text = text.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, "").replace(/<base\b[^>]*>/gi, "");
          const frame = document.createElement("iframe");
          frame.title = file.name; frame.sandbox = "";
          frame.srcdoc = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src ${location.origin} data:;"><base href="${esc(url(file.url))}">` + text;
          view.replaceChildren(frame);
        } else {
          const cut = text.length > 60000;
          view.innerHTML = `<pre class="${file.name.endsWith(".md") ? "prose" : ""}">${esc(cut ? text.slice(0, 60000) : text)}${cut ? "\n\n" + esc(t("cases.truncated")) : ""}</pre>`;
        }
      } catch { view.innerHTML = `<div class="empty-state">${esc(t("doc_failed"))}</div>`; }
    } else view.innerHTML = `<div class="empty-state">${link(file, t("cases.open_file"))}</div>`;
  }
  renderFilters(); selectDomain(domainId);
  addEventListener("hashchange", () => { const id = location.hash.slice(1); if (id !== domainId && data.domains.some(d => d.id === id)) selectDomain(id); });
}

/* ---------- start ---------- */
function renderStart() {
  const choice = $("#template-choice");
  const requested = new URLSearchParams(location.search).get("template");
  if ([...choice.options].some(o => o.value === requested)) choice.value = requested;
  function update() {
    const template = choice.value;
    $("#template-help").innerHTML = `${esc(t("start.pre." + template))} <button class="inline-link" data-doc="${esc(guide("src/rsi_anything/templates/" + template))}">${esc(t("start.template_doc"))} ↗</button>`;
    const install = template === "cpu-classifier" ? "\npython -m pip install -r requirements.txt" : "";
    $("#run-code").textContent = `rsi init ${template} my-rsi-task\ncd my-rsi-task${install}\nrsi check\nrsi run --agent codex --model YOUR_MODEL --rounds 3${template === "video-cut" ? " --jury cli:codex:YOUR_MODEL" : ["svg-drawing", "landing-page"].includes(template) ? " --jury cli:claude --live" : ""}`;
    const next = new URL(location.href); next.searchParams.set("template", template);
    history.replaceState(null, "", next);
  }
  choice.addEventListener("change", update); update();
}

if (page === "home") renderHome();
if (LAB_CASES[page]) {
  $$("[data-case]").forEach(b => b.addEventListener("click", () => { stopPlay(); state.template = b.dataset.case; state.view = "now"; loadCase(); }));
  await loadCase(true);
}
if (page === "cases") renderCases();
if (page === "start") renderStart();
