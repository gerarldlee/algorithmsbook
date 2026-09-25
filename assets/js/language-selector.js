(() => {
  const storageKey = "preferred-language";
  const levelStorageKey = "preferred-level";
  const languages = [
    ["java", "Java"],
    ["c", "C"],
    ["python", "Python"],
    ["rust", "Rust"],
    ["typescript", "TypeScript"],
    ["go", "Go"],
  ];
  const algorithmOrder = languages.map(([value]) => value);
  const levels = [
    ["all", "All"],
    ["normal", "Normal"],
    ["advanced", "Advanced"],
  ];

  function languageOf(code) {
    return code.dataset.lang || code.className.match(/(?:^|\s)language-([^\s]+)/)?.[1];
  }

  function algorithmGroups() {
    const blocks = Array.from(document.querySelectorAll("pre > code"))
      .map((code) => ({
        code,
        language: languageOf(code),
        container: code.closest(".hextra-code-block") || code.closest(".highlight") || code.parentElement,
      }))
      .filter(({ language }) => language);
    const groups = [];

    for (let index = 0; index <= blocks.length - algorithmOrder.length; index += 1) {
      const candidate = blocks.slice(index, index + algorithmOrder.length);
      if (candidate.every(({ language }, offset) => language === algorithmOrder[offset])) {
        groups.push(candidate);
        index += algorithmOrder.length - 1;
      }
    }

    return groups;
  }

  function applyLanguage(language) {
    algorithmGroups().flat().forEach(({ container, language: blockLanguage }) => {
      const hidden = blockLanguage !== language;
      container.hidden = hidden;
      container.dataset.languageFilter = hidden ? "hidden" : "visible";
    });
  }

  function savedLanguage() {
    const saved = window.localStorage.getItem(storageKey);
    return languages.some(([value]) => value === saved) ? saved : "java";
  }

  function savedLevel() {
    const saved = window.localStorage.getItem(levelStorageKey);
    return levels.some(([value]) => value === saved) ? saved : "all";
  }

  function applyLevel(level) {
    const pageContent = document.querySelector("[data-page-level]");
    const pageLevel = pageContent?.dataset.pageLevel;
    const pageVisible = level === "all" || !pageLevel || pageLevel === level;
    if (pageContent) pageContent.hidden = !pageVisible;

    document.querySelectorAll("[data-level]").forEach((section) => {
      const sectionLevel = section.dataset.level;
      section.hidden = !pageVisible || (level !== "all" && sectionLevel !== level);
    });
  }

  function createSelector() {
    const docsLink = document.querySelector(
      '.hextra-nav-container nav a[href$="/docs"], .hextra-nav-container nav a[href$="/docs/"]',
    );
    if (!docsLink) return;

    const selector = document.createElement("select");
    selector.className = "language-selector";
    selector.setAttribute("aria-label", "Preferred programming language");
    selector.title = "Preferred programming language";

    languages.forEach(([value, label]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      selector.appendChild(option);
    });

    selector.value = savedLanguage();
    selector.addEventListener("change", () => {
      window.localStorage.setItem(storageKey, selector.value);
      applyLanguage(selector.value);
    });

    const levelSelector = document.createElement("select");
    levelSelector.className = "level-selector";
    levelSelector.setAttribute("aria-label", "Topic level");
    levelSelector.title = "Topic level";

    levels.forEach(([value, label]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      levelSelector.appendChild(option);
    });
    levelSelector.value = savedLevel();
    levelSelector.addEventListener("change", () => {
      window.localStorage.setItem(levelStorageKey, levelSelector.value);
      applyLevel(levelSelector.value);
    });

    docsLink.before(selector);
    docsLink.before(levelSelector);
    applyLanguage(selector.value);
    applyLevel(levelSelector.value);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createSelector);
  } else {
    createSelector();
  }
})();
