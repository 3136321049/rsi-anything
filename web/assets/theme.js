// 首帧前恢复访客手动选择的深浅主题（站点 CSP 不允许内联脚本，所以单独成文件、同步加载）。
try {
  const mode = localStorage.getItem("darwin-theme");
  if (mode === "dark" || mode === "light") document.documentElement.dataset.theme = mode;
} catch { /* 无痕模式 */ }
