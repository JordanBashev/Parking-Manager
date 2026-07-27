// Clean-path client-side router over the History API. Routes are matched to a
// screen module; the dev server falls back to index.html so deep links refresh
// cleanly. Screens receive any captured path params.

const routes = [];

// The app may be served from a subdirectory (GitHub Pages serves it at
// /<repo>/), so routes are matched against the path *below* that directory.
// import.meta.url points at /js/router.js, so its grandparent is the app root.
const BASE_PATH = new URL("../", import.meta.url).pathname.replace(/\/$/, "");

// "/Parking-Manager/place/1" → "/place/1"
function toRoutePath(pathname) {
  const path = pathname.startsWith(BASE_PATH) ? pathname.slice(BASE_PATH.length) : pathname;
  return path || "/";
}

// "/place/1" → "/Parking-Manager/place/1"
function toUrlPath(routePath) {
  return BASE_PATH + routePath;
}

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
  const url = toUrlPath(path);
  if (url !== location.pathname) history.pushState({}, "", url);
  resolve();
}

export function resolve() {
  const path = toRoutePath(location.pathname || "/");
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
