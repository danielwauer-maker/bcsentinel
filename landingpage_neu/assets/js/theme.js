(function () {
  const KEY = "bcsentinel-theme";

  function currentTheme() {
    try {
      const saved = localStorage.getItem(KEY);
      if (saved === "light" || saved === "dark") return saved;
    } catch (_) {}
    return "light";
  }

  function applyTheme(theme) {
    const selected = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", selected);
    try { localStorage.setItem(KEY, selected); } catch (_) {}
    document.querySelectorAll("[data-theme-icon]").forEach((node) => {
      node.textContent = selected === "dark" ? "L" : "D";
    });
  }

  window.BCSentinelTheme = {
    currentTheme,
    applyTheme,
    toggle: () => applyTheme(currentTheme() === "dark" ? "light" : "dark"),
  };

  applyTheme(currentTheme());
})();
