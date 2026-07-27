// The sticky top bar. Nav links depend on role: a worker sees only "My places";
// an admin also sees Hotels, Users, Reports. A worker is never offered admin
// routes. Hidden entirely on the login screen.

import { api } from "./api.js";
import { navigate } from "./router.js";
import { isAdmin, state } from "./state.js";
import { el } from "./ui.js";

const ADMIN_LINKS = [
  ["All places", "/"],
  ["Hotels", "/hotels"],
  ["Users", "/users"],
  ["Reports", "/reports"],
];
const WORKER_LINKS = [["My places", "/"]];

function linkStyle(active) {
  return active
    ? "color: var(--color-accent); border-bottom: 2px solid var(--color-accent); padding-bottom: 2px"
    : "color: color-mix(in srgb, var(--color-text) 75%, transparent); border-bottom: 2px solid transparent; padding-bottom: 2px";
}

function isActive(href) {
  if (href === "/") return location.pathname === "/" || location.pathname.startsWith("/place");
  return location.pathname.startsWith(href);
}

export function renderNav() {
  const root = document.getElementById("nav");
  if (!state.session) {
    root.replaceChildren();
    return;
  }

  const links = (isAdmin() ? ADMIN_LINKS : WORKER_LINKS).map(([label, href]) =>
    el("a", {
      href,
      "data-link": "",
      style: `${linkStyle(isActive(href))}; font-size: 14px`,
    }, label)
  );

  const user = el("div", { style: "text-align: right; line-height: 1.25" }, [
    el("div", { style: "font-size: 13px" }, state.session.first_name),
    el(
      "div",
      {
        style:
          "font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: color-mix(in srgb, var(--color-text) 50%, transparent)",
      },
      state.session.role
    ),
  ]);

  const signOut = el(
    "button",
    {
      class: "btn btn-secondary",
      onClick: async () => {
        await api.post("/auth/logout");
        state.session = null;
        navigate("/login");
      },
    },
    "Sign out"
  );

  root.replaceChildren(
    el(
      "div",
      {
        class: "nav",
        style:
          "border-bottom: 1px solid var(--color-divider); padding: 10px 24px; gap: 24px; position: sticky; top: 0; background: var(--color-bg); z-index: 5",
      },
      [
        el("div", { class: "nav-brand", style: "letter-spacing: 0.02em; margin-right: 28px" }, "MANAGINING"),
        ...links,
        el("div", { style: "margin-left: auto; display: flex; align-items: center; gap: 14px" }, [
          user,
          signOut,
        ]),
      ]
    )
  );
}
