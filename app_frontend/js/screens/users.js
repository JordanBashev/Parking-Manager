// Users (admin) — create worker accounts and list all accounts. Admins are
// provisioned outside the app, so this only creates workers.

import { api, ApiError } from "../api.js";
import { contentColumn, dataTable } from "../layout.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { blueprint, el, primaryButton, toast } from "../ui.js";

// UserRead.created is an ISO datetime; the table shows dd/mm/yyyy.
function isoDateTimeToDisplay(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value || "");
  return match ? `${match[3]}/${match[2]}/${match[1]}` : (value || "");
}

export async function renderUsers() {
  renderNav();
  const main = document.getElementById("main");

  let users;
  try {
    users = await api.get("/users");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return navigate("/login");
    if (error instanceof ApiError && error.status === 403) return navigate("/");
    throw error;
  }

  const draft = { username: "", first_name: "", password: "" };
  const field = (label, type, key) => {
    const input = el("input", {
      class: "input",
      type: type || "text",
      onInput: (e) => (draft[key] = e.target.value),
      onKeydown: (e) => e.key === "Enter" && create(),
    });
    return el("div", { class: "field" }, [el("label", {}, label), input]);
  };

  async function create() {
    if (!draft.username.trim() || !draft.first_name.trim() || !draft.password.trim()) {
      toast("Username, first name and password are all required");
      return;
    }
    try {
      await api.post("/users", {
        username: draft.username.trim(),
        first_name: draft.first_name.trim(),
        password: draft.password,
      });
      toast("Worker account created");
      renderUsers();
    } catch (error) {
      toast(error instanceof ApiError && error.status === 409 ? "That username is already taken." : "Could not create the account.");
    }
  }

  const createRow = blueprint({ class: "grid-2col-mobile", style: "padding: 14px; margin: 18px 0 22px; display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 12px; align-items: end" }, [
    field("Username", "text", "username"),
    field("First name", "text", "first_name"),
    field("Password", "password", "password"),
    primaryButton("Create worker", create, { height: "36px" }),
  ]);

  const columns = [
    { label: "Username", cellStyle: "font-family: var(--font-heading); font-size: 15px" },
    { label: "First name" },
    { label: "Role", style: "width: 120px" },
    { label: "Created", style: "width: 120px", cellStyle: "font-variant-numeric: tabular-nums" },
  ];

  const rows = users.map((user) => [
    user.username,
    user.first_name,
    el("span", { class: user.role === "admin" ? "tag tag-accent" : "tag tag-neutral" }, user.role),
    isoDateTimeToDisplay(user.created),
  ]);

  main.replaceChildren(
    contentColumn([
      el("h2", { style: "margin: 0" }, "Users"),
      el("p", { class: "text-muted", style: "font-size: 13px" }, "Worker accounts are created here. Admin accounts are provisioned outside the app."),
      createRow,
      dataTable(columns, rows),
    ], 760)
  );
}
