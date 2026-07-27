// Frontend runtime config. No build step, so this is a plain module constant.
//
// The backend serves this app, so the API is always on the page's own origin —
// whether that is http://localhost:8000 or the Cloudflare tunnel's HTTPS URL.
// A relative base therefore needs no edit when the tunnel URL changes, and it
// keeps the session cookie first-party (browsers block third-party cookies).

export const API_BASE = "/api";
