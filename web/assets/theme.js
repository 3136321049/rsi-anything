// Restore the visitor's chosen light/dark theme before the first paint (the site CSP forbids inline scripts, so this is a separate, synchronously loaded file).
try {
  const mode = localStorage.getItem("darwin-theme");
  if (mode === "dark" || mode === "light") document.documentElement.dataset.theme = mode;
} catch { /* private browsing */ }
