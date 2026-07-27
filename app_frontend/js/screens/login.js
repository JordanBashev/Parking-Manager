// Login — the only screen without a session. On success it loads the session and
// lands on the places list. No demo role toggle: role comes from the account.

import { api, ApiError } from "../api.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { state } from "../state.js";
import { blueprint, el, fieldError } from "../ui.js";

export function renderLogin() {
  renderNav(); // clears the bar
  const main = document.getElementById("main");

  let username = "";
  let password = "";

  const errorSlot = el("div");

  function setError(message) {
    errorSlot.replaceChildren(
      message
        ? el(
            "div",
            {
              style:
                "font-size: 12px; color: var(--color-accent-800); background: var(--color-accent-100); padding: 6px 9px",
            },
            message
          )
        : null
    );
  }

  async function submit() {
    if (!username.trim() || !password.trim()) {
      setError("Enter a username and password.");
      return;
    }
    try {
      state.session = await api.post("/auth/login", { username, password });
      navigate("/");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setError("Username or password is incorrect.");
      } else {
        setError("Could not sign in. Try again.");
      }
    }
  }

  const usernameInput = el("input", {
    id: "lg-u",
    class: "input",
    autocomplete: "username",
    onInput: (event) => (username = event.target.value),
    onKeydown: (event) => event.key === "Enter" && submit(),
  });
  const passwordInput = el("input", {
    id: "lg-p",
    class: "input",
    type: "password",
    autocomplete: "current-password",
    onInput: (event) => (password = event.target.value),
    onKeydown: (event) => event.key === "Enter" && submit(),
  });

  const card = blueprint({ class: "card", style: "padding: 22px; gap: 14px" }, [
    el("div", { class: "field" }, [el("label", { for: "lg-u" }, "Username"), usernameInput]),
    el("div", { class: "field" }, [el("label", { for: "lg-p" }, "Password"), passwordInput]),
    errorSlot,
    el(
      "button",
      { class: "btn btn-primary btn-block blueprint", style: "height: 38px", onClick: submit },
      [el("i", { class: "corner tl" }), el("i", { class: "corner tr" }), el("i", { class: "corner bl" }), el("i", { class: "corner br" }), "Sign in"]
    ),
  ]);

  const wordmark = el("div", { style: "display: flex; align-items: baseline; gap: 8px; margin-bottom: 22px" }, [
    el("div", { style: "font-family: var(--font-heading); font-size: 22px; letter-spacing: 0.02em" }, "MANAGINING"),
    el(
      "div",
      { style: "font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: color-mix(in srgb, var(--color-text) 50%, transparent)" },
      "Internal"
    ),
  ]);

  main.replaceChildren(
    el("div", { style: "min-height: 100vh; display: grid; place-items: center; padding: 40px" }, [
      el("div", { style: "width: 340px" }, [wordmark, card]),
    ])
  );
  usernameInput.focus();
}
