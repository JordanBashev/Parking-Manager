// Frontend runtime config. No build step, so this is a plain module constant.
//
// The frontend runs from two places with two different backends:
//   • locally (http://localhost:5173) → the backend is on localhost:8000
//   • on GitHub Pages (https://…github.io) → the backend is your PC, reached
//     through the Cloudflare tunnel's public HTTPS URL
//
// The tunnel URL changes every time you restart `cloudflared` (the free quick
// tunnel), so when it changes, update TUNNEL_API_BASE below and redeploy the
// frontend (a git push to the Pages branch).

const TUNNEL_API_BASE = "https://REPLACE-ME.trycloudflare.com/api";

const isLocal =
  location.hostname === "localhost" || location.hostname === "127.0.0.1";

export const API_BASE = isLocal ? "http://localhost:8000/api" : TUNNEL_API_BASE;
