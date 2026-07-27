// Boot: resolve the session, register routes, start the router. A missing session
// sends every route to /login; the login screen itself needs no session.

import { api, ApiError } from "./api.js";
import { navigate, resolve, route, startRouter } from "./router.js";
import { state } from "./state.js";
import { renderLogin } from "./screens/login.js";
import { renderPlaces } from "./screens/places.js";
import { renderPlace } from "./screens/place.js";
import { renderHotels } from "./screens/hotels.js";
import { renderUsers } from "./screens/users.js";
import { renderReports } from "./screens/reports.js";

// Wrap a screen so it redirects to /login when there is no session.
function guarded(render) {
  return (params) => {
    if (!state.session) return navigate("/login");
    return render(params);
  };
}

route("/login", renderLogin);
route("/", guarded(renderPlaces));
route("/place/:id", guarded(renderPlace));
route("/hotels", guarded(renderHotels));
route("/users", guarded(renderUsers));
route("/reports", guarded(renderReports));

async function boot() {
  try {
    state.session = await api.get("/auth/me");
  } catch (error) {
    state.session = null;
  }

  startRouter();

  // If we loaded on /login but already have a session, go home; and vice versa.
  if (!state.session && location.pathname !== "/login") {
    navigate("/login");
  } else if (state.session && location.pathname === "/login") {
    navigate("/");
  } else {
    resolve();
  }
}

boot();
