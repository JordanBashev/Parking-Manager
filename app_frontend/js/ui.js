// Shared rendering helpers. `el` is a tiny DOM builder used everywhere instead
// of innerHTML, so event wiring stays attached and there is no injection risk.

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "style" && typeof value === "object") {
      Object.assign(node.style, value);
    } else if (key === "class") {
      node.className = value;
    } else if (key === "dataset") {
      Object.assign(node.dataset, value);
    } else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key in node && key !== "list") {
      node[key] = value;
    } else {
      node.setAttribute(key, value);
    }
  }
  for (const child of [].concat(children)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

// The four "+" registration marks every framed object wears.
export function corners() {
  return ["tl", "tr", "bl", "br"].map((pos) => el("i", { class: `corner ${pos}` }));
}

// A blueprint frame: transparent line-drawing box with corner marks.
export function blueprint(attrs, children) {
  const { class: klass = "", ...rest } = attrs || {};
  return el("div", { class: `blueprint ${klass}`.trim(), ...rest }, [
    ...corners(),
    ...[].concat(children || []),
  ]);
}

// The one solid accent button, also framed with corner marks.
export function primaryButton(label, onClick, extraStyle = {}) {
  return el(
    "button",
    { class: "btn btn-primary blueprint", onClick, style: extraStyle },
    [...corners(), label]
  );
}

let toastTimer;
export function toast(message) {
  const root = document.getElementById("toast-root");
  root.replaceChildren(
    blueprint(
      {
        style: {
          position: "fixed",
          bottom: "22px",
          left: "50%",
          transform: "translateX(-50%)",
          background: "var(--color-accent-900)",
          color: "var(--color-bg)",
          padding: "9px 16px",
          fontSize: "13px",
          boxShadow: "var(--shadow-md)",
          zIndex: "20",
        },
      },
      message
    )
  );
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => root.replaceChildren(), 2200);
}

export function closeDialog() {
  document.getElementById("dialog-root").replaceChildren();
}

// A modal over its backdrop. `bodyNodes` may include an input for the "new place"
// dialog; `confirmLabel`/`onConfirm` drive the primary action.
export function openDialog({ title, body, bodyNodes = [], confirmLabel, onConfirm }) {
  const root = document.getElementById("dialog-root");
  const dialog = blueprint(
    { class: "dialog", style: { background: "var(--color-bg)" } },
    [
      el("div", { class: "dialog-title" }, title),
      el("div", { class: "dialog-body" }, body),
      ...bodyNodes,
      el("div", { class: "dialog-actions" }, [
        el("button", { class: "btn btn-secondary", onClick: closeDialog }, "Cancel"),
        primaryButton(confirmLabel, onConfirm),
      ]),
    ]
  );
  root.replaceChildren(el("div", { class: "dialog-backdrop" }, dialog));
}

export function fieldError(message) {
  return message
    ? el(
        "div",
        {
          style: {
            fontSize: "11px",
            color: "var(--color-accent-800)",
            marginTop: "4px",
          },
        },
        message
      )
    : null;
}
