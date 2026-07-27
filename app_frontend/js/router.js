// Clean-path client-side router over the History API. Routes are matched to a
// screen module; the dev server falls back to index.html so deep links refresh
// cleanly. Screens receive any captured path params.

const routes = [];

export function route(pattern, handler) {
  // "/place/:id" → regex with a named group.
  const names = [];
  const regex = new RegExp(
    "^" +
      pattern.replace(/:[^/]+/g, (match) => {
        names.push(match.slice(1));
        return "([^/]+)";
      }) +
      "/?$"
  );
  routes.push({ regex, names, handler });
}

export function navigate(path) {
  if (path !== location.pathname) history.pushState({}, "", path);
  resolve();
}

export function resolve() {
  const path = location.pathname || "/";
  for (const { regex, names, handler } of routes) {
    const match = regex.exec(path);
    if (match) {
      const params = {};
      names.forEach((name, index) => (params[name] = decodeURIComponent(match[index + 1])));
      handler(params);
      return;
    }
  }
  // Unknown path → home.
  navigate("/");
}

// Attach navigation listeners. The caller performs the initial resolve() so boot
// can decide login-vs-home first without a double render.
export function startRouter() {
  window.addEventListener("popstate", resolve);
  // Intercept in-app links marked data-link for clean-path navigation.
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[data-link]");
    if (!link) return;
    event.preventDefault();
    navigate(link.getAttribute("href"));
  });
}
