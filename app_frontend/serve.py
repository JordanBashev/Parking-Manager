"""Static dev server for the standalone frontend, with SPA fallback.

Clean-path routing means a refresh on /place/123 must still return index.html
rather than 404. Python's plain http.server can't do that, so this thin wrapper
serves real files and falls back to index.html for unknown paths.

Stdlib only — run it through the project's .venv, no extra dependency:
    python app_frontend/serve.py            (defaults to port 5173)
    python app_frontend/serve.py 5000
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent
DEFAULT_PORT = 5173


class SpaRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        requested = (FRONTEND_DIR / self.path.lstrip("/").split("?")[0]).resolve()
        # Serve the file if it exists inside the frontend dir; otherwise the SPA
        # entry, so deep links and refreshes resolve client-side.
        if not (requested.is_file() and FRONTEND_DIR in requested.parents):
            self.path = "/index.html"
        super().do_GET()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    handler = partial(SpaRequestHandler, directory=str(FRONTEND_DIR))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Frontend on http://127.0.0.1:{port}  (serving {FRONTEND_DIR})")
        server.serve_forever()


if __name__ == "__main__":
    main()
