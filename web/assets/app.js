  const BASE = new URL("../", import.meta.url);
  const page = document.body.dataset.page;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const url = path => new URL(path, BASE).href;
  const number = value => value == null ? "—" : Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 3 });
  const clock = seconds => `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
  const labels = { BASELINE: "初始版本", KEEP: "保留", REVERT: "拒绝", NO_CHANGE: "无正式改动", AGENT_FAIL: "执行失败", JUDGE_FAIL: "评审失败" };
  const stateClass = s => s === "KEEP" ? "keep" : s === "REVERT" ? "revert" : "";
  let toastTimer, current, selected = 0, loadId = 0;
  const state = { template: page === "code" ? "code-speed" : page === "experiments" ? "cpu-classifier" : "video-cut", mode: "split", compare: "baseline" };
  const params = new URLSearchParams(location.search);
  if (page === "code" && ["code-speed", "code-repair"].includes(params.get("case"))) state.template = params.get("case");
  if (["diff", "split"].includes(params.get("view"))) state.mode = params.get("view");
  if (params.get("compare") === "previous") state.compare = "previous";

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
      toast("已复制");
    } catch { toast("暂时无法自动复制，请手动选择内容复制。"); }
  }
  const dialog = $("#media-dialog");
  let dialogFocus;
  function openDialog(title, content) {
    dialogFocus = document.activeElement;
    $("#dialog-title").textContent = title;
    $("#dialog-content").innerHTML = content;
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
  $(".menu-toggle").addEventListener("click", () => {
    const open = $("#main-nav").classList.toggle("open");
    $(".menu-toggle").setAttribute("aria-expanded", String(open));
    $(".menu-toggle").setAttribute("aria-label", open ? "关闭导航" : "打开导航");
  });
  $$("#main-nav a").forEach(a => a.addEventListener("click", () => { $("#main-nav").classList.remove("open"); $(".menu-toggle").setAttribute("aria-expanded", "false"); $(".menu-toggle").setAttribute("aria-label", "打开导航"); }));
  document.addEventListener("keydown", e => { if (e.key === "Escape") { $("#main-nav").classList.remove("open"); $(".menu-toggle").setAttribute("aria-expanded", "false"); $(".menu-toggle").setAttribute("aria-label", "打开导航"); } });
  document.addEventListener("click", async e => {
    const button = e.target.closest("[data-copy],[data-copy-target],[data-demo],[data-doc],[data-image]");
    if (!button) return;
    if (button.hasAttribute("data-copy")) await copy(button.dataset.copy);
    else if (button.dataset.copyTarget) await copy($("#" + button.dataset.copyTarget).textContent);
    else if (button.hasAttribute("data-demo")) {
      openDialog("35 秒 · 真实作品演示", `<video controls playsinline preload="metadata" poster="${url("assets/demo-poster.jpg")}" src="${url("examples/showcase-media/openrsi-demo.mp4")}"></video><p class="subtle">由保存的代码修复、写作手册、视频剪辑与分类错例组成。35 秒，无声。<a href="${url("examples/showcase-media/demo-video.json")}" target="_blank" rel="noopener">查看素材来源 ↗</a></p>`);
    } else if (button.dataset.image) openDialog(button.dataset.title || "作品图片", `<img src="${esc(button.dataset.image)}" alt="${esc(button.dataset.title || "作品图片")}">`);
    else if (button.dataset.doc) await showDoc(button.dataset.doc);
  });
  document.addEventListener("play", e => { if (e.target.tagName === "VIDEO") $$("video").forEach(v => { if (v !== e.target) v.pause(); }); }, true);
  document.addEventListener("error", e => {
    if (e.target.tagName === "VIDEO") {
      const note = document.createElement("p"); note.className = "video-error subtle";
      note.textContent = "视频暂时无法播放，请检查连接，或下载原文件后查看。";
      if (!e.target.nextElementSibling?.classList.contains("video-error")) e.target.after(note);
    }
  }, true);

  function docInline(text, docPath) {
    let value = esc(text).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    return value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      const decoded = href.replace(/&amp;/g, "&");
      let target;
      try { target = new URL(decoded, url(docPath)); } catch { return label; }
      if (!["https:", "http:"].includes(target.protocol)) return label;
      const local = target.origin === BASE.origin && target.pathname.startsWith(BASE.pathname);
      const doc = local && target.pathname.endsWith(".md");
      return doc ? `<button class="text-button inline-link" data-doc="${esc(target.pathname.slice(BASE.pathname.length))}">${label}</button>` : `<a href="${esc(target.href)}" target="_blank" rel="noopener">${label}</a>`;
    });
  }
  function markdown(text, path) {
    const lines = text.replace(/\r/g, "").split("\n");
    let html = "", fence = false, code = [], table = [];
    function flushTable() {
      if (!table.length) return;
      const rows = table.filter(line => !/^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(line));
      html += `<table>${rows.map((line, i) => "<tr>" + line.replace(/^\s*\||\|\s*$/g, "").split("|").map(cell => `<${i ? "td" : "th"}>${docInline(cell.trim(), path)}</${i ? "td" : "th"}>`).join("") + "</tr>").join("")}</table>`;
      table = [];
    }
    for (const line of lines) {
      if (line.startsWith("```")) { flushTable(); if (fence) { html += `<pre><code>${esc(code.join("\n"))}</code></pre>`; code = []; } fence = !fence; continue; }
      if (fence) { code.push(line); continue; }
      if (line.trim().startsWith("|")) { table.push(line); continue; }
      flushTable();
      const heading = /^(#{1,3}) (.*)/.exec(line);
      if (heading) html += `<h${heading[1].length}>${docInline(heading[2], path)}</h${heading[1].length}>`;
      else if (/^\s*[-*] /.test(line)) html += `<p>• ${docInline(line.replace(/^\s*[-*] /, ""), path)}</p>`;
      else if (line.trim()) html += `<p>${docInline(line, path)}</p>`;
    }
    flushTable();
    if (code.length) html += `<pre>${esc(code.join("\n"))}</pre>`;
    return html;
  }
  async function showDoc(path) {
    try {
      const response = await fetch(url(path));
      if (!response.ok) throw new Error("missing");
      const text = await response.text();
      openDialog("使用说明与原始记录", `<div class="document-view">${markdown(text, path)}<a class="raw-doc-link" href="${esc(url(path))}" target="_blank" rel="noopener">打开原始 Markdown 文件 ↗</a></div>`);
    } catch { toast("这份说明暂时无法读取，请稍后重试。"); }
  }

  function syncAddress() {
    const next = new URL(location.href);
    next.search = "";
    next.searchParams.set("round", selected);
    if (page === "code") {
      next.searchParams.set("case", state.template);
      if (state.mode !== "split") next.searchParams.set("view", state.mode);
      if (state.compare !== "baseline") next.searchParams.set("compare", state.compare);
    }
    history.replaceState(null, "", next);
  }
  function badge(row) { return `<span class="state-pill ${stateClass(row.status)}">${labels[row.status] || esc(row.status)}${row.round === current.best_round && row.round > 0 ? " · 最终保留" : ""}</span>`; }
  function roundNav() {
    return `<div class="round-header"><h2>沿着轮次，看看发生了什么</h2><span>点选任一轮查看作品与理由</span></div><div class="round-nav" aria-label="实验轮次">${current.rounds.map(row => `<button class="round-button ${selected === row.round ? "active" : ""}" data-round="${row.round}" aria-pressed="${selected === row.round}"><span>${row.round ? "第 " + row.round + " 轮" : "初始版本"}</span><strong>${number(row.score)}<small>${row.score == null ? "" : esc(current.unit)}</small></strong>${badge(row)}</button>`).join("")}</div>`;
  }
  function note(row) {
    return `<div class="experiment-note ${row.status === "REVERT" || !row.formal ? "warning" : ""}"><strong>${row.round ? (row.status === "NO_CHANGE" ? "本轮未产生正式新结果" : row.status === "REVERT" ? "本轮候选未被保留" : "本轮修改已被保留") : "从初始作品建立比较基准"}</strong><p>${esc(row.hypothesis || "固定输入与评价条件，保存初始作品与结果。")}</p>${row.note ? `<p>${esc(row.note)}</p>` : ""}${!row.formal ? `<p>下方继续展示第 ${row.previous_best} 轮的保留结果，不把内部试验输出当作本轮正式作品。</p>` : ""}</div>`;
  }
  function actions() {
    return `<div class="lab-actions"><a class="button dark" href="${url("downloads/" + current.template + ".zip")}" download>下载完整实验结果 <span>↓</span></a><button id="share-run">复制当前比较链接 ↗</button><a class="button outline" href="${url("start/?template=" + current.template)}">使用这个任务 →</a></div>`;
  }
  function evidence() {
    const limitations = current.template === "code-speed"
      ? "结果来自历史运行，同一批名称允许复用预处理；每轮计时受机器与随机输入影响。源码由原始补丁重建并通过独立正确性检查。后续复测不替换历史曲线。"
      : current.template === "cpu-classifier"
        ? "固定验证集包含 450 张数字，训练集为 1347 张。验证集被反复用于选择配置，当前结果不代表新数据上的泛化能力。无修改轮次没有正式新分数。"
        : current.template === "video-cut"
          ? "素材为 Wikimedia Commons 标注公共领域的历史演讲节选。评分主要评价剪后文字的选段与结构；音轨、时长和解码另有验证，不将文字分数当作完整视听质量。"
          : "合成的 Python 记账项目。固定测试检查金额精度、分账余数和月度汇总。结果只说明本例固定测试的修复情况。";
    const verification = current.template === "code-speed" ? "artifact-verification.json" : "verification.json";
    return `<div class="evidence-section"><details><summary>任务条件与结果范围</summary><div class="evidence-body">${limitations}<p>请求模型：${esc(current.requested_model || "历史记录未固定")}；服务端确认型号：${esc(current.actual_model || "未返回")}。没有记录的调用费用保持未知。</p></div></details><details><summary>原始作品、完整记录与独立验证</summary><div class="evidence-body"><a href="${url(current.root + "ledger.jsonl")}" target="_blank" rel="noopener">完整轮次账本 ↗</a><a href="${url(current.root + verification)}" target="_blank" rel="noopener">独立验证 ↗</a><a href="${url(current.root + "report.html")}" target="_blank" rel="noopener">原始报告 ↗</a><button class="text-button inline-link" data-doc="examples/${esc(current.template)}/README.md">案例与来源说明 ↗</button><p class="mono">RUN / ${esc(current.run_id)}</p></div></details></div>`;
  }
  function chart() {
    const max = Math.max(...current.rounds.map(r => r.score || 0)) * 1.16;
    const points = current.rounds.filter(r => r.score != null).map(row => ({ row, x: 7 + 86 * row.round / Math.max(1, current.rounds.length - 1), y: 12 + 136 * (1 - row.score / max) }));
    return `<div class="chart-card"><div class="panel-title">正式结果 · ${esc(current.metric)}<span>选择圆点查看对应修改</span></div><div class="chart"><svg viewBox="0 0 1000 170" preserveAspectRatio="none" aria-hidden="true">${[40, 90, 148].map(y => `<line x1="60" x2="940" y1="${y}" y2="${y}" stroke="#e2e7d7" stroke-dasharray="3 6"/>`).join("")}<polyline points="${points.map(p => `${p.x * 10},${p.y}`).join(" ")}" fill="none" stroke="#839b68" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>${points.map(p => `<button class="chart-point ${selected === p.row.round ? "active" : ""}" style="left:${p.x}%;bottom:${(170 - p.y) / 170 * 100}%" data-round="${p.row.round}" aria-label="查看${p.row.round ? "第" + p.row.round + "轮" : "初始版本"}，${number(p.row.score)}${esc(current.unit)}"></button><span class="chart-value-label" style="left:${p.x}%;top:${Math.max(0, p.y / 170 * 100 - 17)}%">${number(p.row.score)}${esc(current.unit)}</span>`).join("")}</div><div class="chart-labels">${current.rounds.map(r => `<span>${r.round ? "第 " + r.round + " 轮" : "初始"}</span>`).join("")}</div></div>`;
  }
  function highlight(text) {
    const re = /(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:def|return|for|if|elif|else|in|import|from|class|None|True|False|while|try|except|raise|and|or|not|with|as)\b)/g;
    let result = "", last = 0;
    for (const match of text.matchAll(re)) {
      result += esc(text.slice(last, match.index));
      const kind = match[0].startsWith("#") ? "comment" : /^['"]/.test(match[0]) ? "string" : "keyword";
      result += `<span class="syntax-${kind}">${esc(match[0])}</span>`; last = match.index + match[0].length;
    }
    return result + esc(text.slice(last));
  }
  function codePane(row, label) {
    const content = row.code.split("\n").map((line, i) => `<div class="code-line"><span class="line-number">${i + 1}</span><code>${highlight(line)}</code></div>`).join("");
    return `<div class="code-pane"><div class="code-pane-head"><span>${esc(label)}</span><span>${esc(row.filename)}</span></div><div class="code-content" tabindex="0" aria-label="${esc(label)}源码">${content}</div><div class="code-pane-foot"><span>${row.code.split("\n").length} 行</span><a href="${url(row.files_base + row.filename)}" download>下载此版本 ↓</a></div></div>`;
  }
  function lineDiff(left, right) {
    const a = left.split("\n"), b = right.split("\n");
    if (a.length * b.length > 1500000) return [{ type: "info", text: "文件较长，请使用并排比较。" }];
    const table = Array.from({ length: a.length + 1 }, () => new Uint16Array(b.length + 1));
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
    const metric = repair ? `${row.tests.passed || 6}<small>/ 15</small>` : `${number(row.score)}<small>×</small>`;
    $("#lab-app").innerHTML = `<div class="lab-overview"><div class="result-card"><div class="eyebrow">${repair ? "固定业务测试" : "相对原始实现 · 加速倍数"}</div><div class="big-result">${metric}</div><p>${selected ? "第 " + selected + " 轮的正式结果" : "初始版本的正式结果"}</p><div class="result-subline"><span>${repair ? "从 6 项通过开始" : "初始速度 1×"}</span><strong>${repair ? "固定测试真实执行" : "正确性检查通过"}</strong></div></div>${chart()}</div>${roundNav()}${note(row)}<div class="comparison-toolbar"><h2>查看具体修改</h2><div class="control-group"><select id="comparison-base" aria-label="选择比较基准"><option value="baseline" ${state.compare === "baseline" ? "selected" : ""}>与初始版本比较</option><option value="previous" ${state.compare === "previous" ? "selected" : ""}>与上一保留版本比较</option></select><div class="segmented" aria-label="代码查看方式"><button data-mode="split" class="${state.mode === "split" ? "active" : ""}">并排源码</button><button data-mode="diff" class="${state.mode === "diff" ? "active" : ""}">只看改动</button></div></div></div>${state.mode === "split" ? `<div class="code-comparison">${codePane(left, left.round ? "第 " + left.round + " 轮 · 保留版本" : "初始版本")}${codePane(row, selected ? "第 " + selected + " 轮 · 当前候选" : "初始版本")}</div>` : `<div class="code-pane"><div class="code-pane-head"><span>绿色为新增 · 红色为删除</span><span>${esc(row.filename)}</span></div><div class="code-content" tabindex="0" aria-label="代码修改差异">${lineDiff(left.code, row.code).map((l, i) => `<div class="code-line ${l.type ? "diff-" + l.type : ""}"><span class="line-number">${i + 1}</span><code>${esc(l.text)}</code></div>`).join("")}</div></div>`}<p class="source-note">${repair ? "测试覆盖金额精度、分账余数、月份格式、日期与退款处理。" : "曲线使用原运行的正式测量。历史源码从保存的补丁恢复，后续复测与原始分数分开记录。"}</p>${actions()}${evidence()}`;
    $("#comparison-base").addEventListener("change", e => { state.compare = e.target.value; syncAddress(); renderCode(); bindRounds(); });
    $$("[data-mode]").forEach(b => b.addEventListener("click", () => { state.mode = b.dataset.mode; syncAddress(); renderCode(); bindRounds(); }));
    const panes = $$(".code-content");
    if (panes.length === 2) {
      let syncing = false;
      panes.forEach((pane, i) => pane.addEventListener("scroll", () => {
        if (syncing) return;
        syncing = true; panes[1 - i].scrollTop = pane.scrollTop;
        requestAnimationFrame(() => { syncing = false; });
      }));
    }
  }
  function imageCard(path, title, subtitle) {
    return `<div class="image-card"><div class="image-card-head">${title}<span>${subtitle}</span></div><button data-image="${url(path)}" data-title="${esc(title)}" aria-label="放大${esc(title)}"><img src="${url(path)}" alt="${esc(title)}" loading="lazy"></button><div class="image-card-foot">点击放大 · 原始实验图片</div></div>`;
  }
  function renderModel() {
    const row = current.rounds[selected], original = current.rounds[0], displayed = row.formal ? row : current.rounds[row.previous_best];
    const metrics = displayed.metrics, first = original.metrics, configuration = displayed.configuration;
    let matrix = '<span></span>' + Array.from({ length: 10 }, (_, i) => `<span>${i}</span>`).join("");
    metrics.confusion_matrix.forEach((line, real) => {
      matrix += `<span>${real}</span>`;
      line.forEach((value, predicted) => {
        const light = value ? 91 - Math.min(1, value / 48) * 57 : 96;
        matrix += `<button style="background:hsl(85 21% ${light}%);color:${light < 55 ? "#f6f6ed" : "#6f805a"}" data-cell="${real},${predicted}" aria-label="真实数字${real}，预测为${predicted}，${value}张">${value || "·"}</button>`;
      });
    });
    const keys = [["model", "分类器"], ["scaling", "缩放"], ["pca_components", "PCA 维数"]];
    const configRows = keys.map(([k, label]) => `<tr><td>${label}</td><td>${esc(original.configuration[k])}</td><td>${esc(configuration[k])}</td></tr>`).join("") + `<tr><td>模型参数</td><td>${esc(JSON.stringify(original.configuration.params))}</td><td>${esc(JSON.stringify(configuration.params))}</td></tr>`;
    $("#lab-app").innerHTML = `<div class="model-overview"><div class="result-card"><div class="eyebrow">固定验证集 · 当前展示结果</div><div class="big-result">${number(metrics.accuracy_percent)}<small>%</small></div><p>${displayed.round ? "第 " + displayed.round + " 轮的正式模型" : "初始三层决策树"}</p><div class="result-subline"><span>验证样本 <strong>450</strong></span><span>错分 <strong>${metrics.mistakes}</strong> 张</span><span>CPU 实验</span></div></div><div class="accuracy-lines"><div class="panel-title">从初始预测到当前结果<span>越高越好</span></div>${[[first.accuracy_percent, "初始正确率"], [metrics.accuracy_percent, "当前正确率"]].map(([value, label]) => `<div class="accuracy-row"><div><span>${label}</span><span class="mono">${number(value)}%</span></div><div class="accuracy-track"><i style="width:${value}%"></i></div></div>`).join("")}<p>初始错分 239 张；最终保留模型错分 3 张。后两轮未产生正式新模型。</p></div></div>${roundNav()}${note(row)}<div class="model-grid"><div class="matrix-card"><div class="panel-title">预测分布<span>点击方格筛选样本</span></div><div class="matrix-wrap"><div class="matrix-axis">真实数字</div><div class="matrix" role="group" aria-label="分类混淆矩阵">${matrix}</div></div><div class="matrix-caption">预测数字</div><p>对角线表示预测正确；其他方格是错例。数字为样本数量。</p></div><div class="config-card"><div class="panel-title">模型配置<span>初始 / 当前</span></div><table class="config-table"><thead><tr><th>参数</th><th>初始</th><th>当前</th></tr></thead><tbody>${configRows}</tbody></table><p class="config-note">训练样本 1347 张，验证样本 450 张。评价程序与数据划分在本次运行中固定。</p><p class="config-note">正式训练与预测耗时：${number(metrics.train_predict_seconds)} 秒。耗时依赖设备，不计入准确率分数。</p></div></div><div class="prediction-card"><div class="panel-title">查看具体预测<span>真实标签与模型输出</span></div><div class="prediction-toolbar"><div><label><input id="only-errors" type="checkbox" checked> 只看错例</label><select id="digit-filter" aria-label="按真实数字筛选"><option value="">所有数字</option>${Array.from({ length: 10 }, (_, i) => `<option>${i}</option>`).join("")}</select><button id="clear-filter">重置筛选</button></div><span id="prediction-count"></span></div><div id="prediction-table" class="predictions-table"></div></div><div class="comparison-toolbar"><h2>直接看看，哪些数字认错了</h2><span class="subtle">图片保留原实验样本</span></div><div class="image-comparison">${imageCard(original.files_base + "out/mistakes.png", "初始模型的错例", "展示前 12 张")}${imageCard(displayed.files_base + "out/mistakes.png", "当前模型的错例", metrics.mistakes + " 张错分")}</div>${actions()}${evidence()}`;
    let pair = null;
    function filterPredictions() {
      const only = $("#only-errors").checked, digit = $("#digit-filter").value;
      const matches = displayed.predictions.filter(p => (!only || !p.correct) && (digit === "" || p.expected === Number(digit)) && (!pair || p.expected === pair[0] && p.predicted === pair[1]));
      $("#prediction-count").textContent = `${pair ? "真实 " + pair[0] + " → 预测 " + pair[1] + " · " : ""}${matches.length} 张${matches.length > 80 ? " · 显示前 80 张" : ""}`;
      $("#prediction-table").innerHTML = matches.length ? `<table><thead><tr><th>样本编号</th><th>真实数字</th><th>预测数字</th><th>结果</th></tr></thead><tbody>${matches.slice(0, 80).map(p => `<tr><td class="mono">${p.sample_id}</td><td>${p.expected}</td><td>${p.predicted}</td><td class="${p.correct ? "right-tag" : "wrong-tag"}">${p.correct ? "正确" : "错分"}</td></tr>`).join("")}</tbody></table>` : `<div class="table-empty">当前筛选条件下没有样本。</div>`;
    }
    $("#only-errors").addEventListener("change", filterPredictions);
    $("#digit-filter").addEventListener("change", () => { pair = null; $$("[data-cell]").forEach(b => b.classList.remove("selected")); filterPredictions(); });
    $("#clear-filter").addEventListener("click", () => { pair = null; $("#only-errors").checked = true; $("#digit-filter").value = ""; $$("[data-cell]").forEach(b => b.classList.remove("selected")); filterPredictions(); });
    $$("[data-cell]").forEach(b => b.addEventListener("click", () => { pair = b.dataset.cell.split(",").map(Number); $("#digit-filter").value = ""; $("#only-errors").checked = false; $$("[data-cell]").forEach(x => x.classList.toggle("selected", x === b)); filterPredictions(); }));
    filterPredictions();
  }
  function renderVideo() {
    const row = current.rounds[selected];
    const special = selected === 3;
    const summaries = {
      0: "初剪沿用开场的八个片段，保存作品，建立第一份比较结果。",
      1: "以捍卫自由的决心开场，再进入团结与分裂的对照。保留原讲话第 22 到 31 段，让主题更集中。",
      2: "选择第 8 到 13 段，再连接第 27 到 31 段，尝试组合前后两部分的表达。完整次序见下方字幕。",
      3: "把第 32 到 38 段连成一条更短的片段。内容得分达到 77，但与此前保留作品的直接比较没有获胜。",
      4: "把第 32 到 34 段放在开场，再连接第 27 到 31 段。保留原话，通过重排顺序尝试新的开头。"
    };
    $("#lab-app").innerHTML = `${roundNav()}<div class="cinema"><div class="cinema-top"><span class="mono">${selected ? "ROUND " + String(selected).padStart(2, "0") : "BASELINE"} / 历史讲话剪辑</span>${badge(row)}</div><div class="cinema-body"><div class="player-stage"><video id="cut-player" controls playsinline preload="metadata" poster="${selected === 1 ? url("assets/video-poster.jpg") : ""}" src="${url(row.files_base + "out/cut.mp4")}"><track kind="captions" src="${url(row.files_base + "out/cut.vtt")}" srclang="en" label="英文字幕"></video></div><div class="cinema-info"><div class="eyebrow">THE CURRENT CUT</div><h2>${selected === 1 ? "最后留下的，<br>是这一版。" : special ? "分数更高，<br>这轮仍被拒绝。" : selected ? "一次不同的<br>剪辑尝试。" : "从最初的<br>选段开始。"}</h2><p>${esc(summaries[selected])}</p><div class="video-stats"><div><span>实际时长</span><strong>${row.duration.toFixed(1)}<small>秒</small></strong></div><div><span>内容评审</span><strong>${number(row.score)}<small>分</small></strong></div><div><span>选取片段</span><strong>${row.segments.length}<small>段</small></strong></div></div><div class="cue-heading">成片字幕<span>点句子跳到对应画面</span></div><div class="cue-list" aria-label="成片字幕">${row.cues.map((cue, i) => `<button class="cue" data-cue="${i}"><time>${clock(cue.start)}</time><span>${esc(cue.text)}</span></button>`).join("")}</div></div></div></div><div class="experiment-note ${row.status === "REVERT" ? "warning" : ""}"><strong>${special ? "这次选择，不能只看分数" : selected === 1 ? "第 1 轮成为最终保留版本" : selected ? "本轮的选择理由" : "初始作品与评价"}</strong><p>${special ? "候选得分 77，高于当时保留版本的 75.5；但交换顺序的两次直接比较均未获胜，因此没有替换保留版本。" : esc(row.note || "固定素材、转写和简报，保存初剪与评审结果。")}</p><p>内容评分主要基于剪后文字，完整视听体验请直接播放比较。</p></div><div class="video-context"><div><h3>这轮选了哪些原始片段？</h3><p>片段编号对应原素材的固定转写。当前排列顺序如下。</p><div class="segment-map">${row.segments.map(id => `<span>${id}</span>`).join("")}</div><a class="inline-link" href="${url(row.files_base + "edit.json")}" target="_blank" rel="noopener">查看剪辑方案 ↗</a></div><details id="original-video"><summary>打开原始素材，对照听一听 ＋</summary><p>1961 年肯尼迪就职演说节选，原素材约 5 分 30 秒。</p><video controls playsinline preload="none" src="${url("examples/video-cut/inputs/public-speech/input.mp4")}"></video><p class="video-compare-hint">播放一个视频时，另一个会自动暂停。</p></details></div><div class="lab-actions"><a class="button dark" href="${url(row.files_base + "out/cut.mp4")}" download>下载当前成片 ↓</a><a class="button outline" href="${url(row.files_base + "out/cut.srt")}" download>下载字幕 ↓</a><button id="share-run">复制当前版本链接 ↗</button><a class="button outline" href="${url("downloads/video-cut.zip")}" download>完整实验记录 ↓</a></div>${evidence()}`;
    const video = $("#cut-player");
    $$("[data-cue]").forEach(b => b.addEventListener("click", () => {
      video.currentTime = row.cues[Number(b.dataset.cue)].start;
      video.play().catch(() => toast("点击播放器的播放按钮继续。"));
    }));
    video.addEventListener("timeupdate", () => {
      const time = video.currentTime;
      $$("[data-cue]").forEach(b => {
        const cue = row.cues[Number(b.dataset.cue)];
        b.classList.toggle("active", time >= cue.start && time < cue.end);
      });
    });
    $("#original-video").addEventListener("toggle", e => { if (!e.target.open) $("video", e.target).pause(); });
  }

  function render() {
    if (page === "code") renderCode();
    if (page === "experiments") renderModel();
    if (page === "video") renderVideo();
    bindRounds();
  }
  function bindRounds() {
    const strip = $(".round-nav"), active = $(".round-button.active");
    if (strip && active && strip.scrollWidth > strip.clientWidth) {
      strip.scrollLeft += active.getBoundingClientRect().left - strip.getBoundingClientRect().left - (strip.clientWidth - active.clientWidth) / 2;
    }
    $$("[data-round]").forEach(b => b.addEventListener("click", () => { selected = Number(b.dataset.round); syncAddress(); render(); }));
    $("#share-run")?.addEventListener("click", () => copy(location.href));
  }
  async function loadCase(fromUrl = false) {
    const id = ++loadId;
    $$("[data-case]").forEach(b => { b.classList.toggle("active", b.dataset.case === state.template); b.setAttribute("aria-pressed", String(b.dataset.case === state.template)); });
    try {
      const response = await fetch(url("data/" + state.template + ".json"));
      if (!response.ok) throw new Error("missing");
      const data = await response.json();
      if (id !== loadId) return;
      current = data;
      const round = Number(new URLSearchParams(location.search).get("round"));
      selected = fromUrl && new URLSearchParams(location.search).has("round") && Number.isInteger(round) && current.rounds.some(r => r.round === round) ? round : current.best_round;
      syncAddress(); render();
    } catch {
      if (id !== loadId) return;
      $("#lab-app").innerHTML = '<div class="load-error"><h2>实验记录暂时没有加载出来。</h2><p>检查网络连接后重试。原始作品仍保存在完整案例中。</p><button id="retry-load">重新加载</button></div>';
      $("#retry-load").addEventListener("click", () => loadCase(true));
    }
  }
  $$("[data-case]").forEach(b => b.addEventListener("click", () => { state.template = b.dataset.case; loadCase(); }));
  if (["code", "experiments", "video"].includes(page)) await loadCase(true);

  if (page === "start") {
    const choice = $("#template-choice");
    const requested = new URLSearchParams(location.search).get("template");
    if ([...choice.options].some(o => o.value === requested)) choice.value = requested;
    function updateTemplate() {
      const template = choice.value;
      const prerequisites = {
        "code-repair": "固定 Python 测试，无额外领域依赖。准备一个已登录的个人编程助手即可开始。",
        "code-speed": "使用本地 Python 检查结果和测量速度。耗时取决于设备，先从默认任务开始。",
        "cpu-classifier": "在任务目录安装 requirements.txt 中的训练依赖，使用 CPU 运行分类实验。",
        "video-cut": "需要 FFmpeg、ffprobe、已准备的视频和转写，以及可用的模型评委。先按模板说明准备素材。"
      };
      $("#template-help").innerHTML = `${prerequisites[template]} <button class="text-button inline-link" data-doc="src/rsi_anything/templates/${template}/README.md">打开模板详细说明 ↗</button>`;
      const install = template === "cpu-classifier" ? "\npython -m pip install -r requirements.txt" : "";
      $("#run-code").textContent = `rsi init ${template} ../my-rsi-task\ncd ../my-rsi-task${install}\nrsi check\nrsi run --agent codex --model YOUR_MODEL --rounds 3${template === "video-cut" ? " --jury cli:codex:YOUR_MODEL" : ""}`;
      const next = new URL(location.href); next.searchParams.set("template", template);
      history.replaceState(null, "", next);
    }
    choice.addEventListener("change", updateTemplate); updateTemplate();
  }