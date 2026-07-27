// Shared layout pieces used by the signed-in screens.

import { blueprint, el } from "./ui.js";

// The centered content column every app screen renders into.
export function contentColumn(children, maxWidth) {
  const style = `max-width: ${maxWidth || 1180}px; margin: 0 auto; padding: 28px 24px 72px`;
  return el("div", { style }, [].concat(children));
}

// A table wrapped in a blueprint frame. `columns` describes headers; `rows` is a
// list of arrays of cell nodes/strings matching the columns.
export function dataTable(columns, rows, wrapperStyle = "padding: 4px 14px 8px") {
  const head = el(
    "thead",
    {},
    el(
      "tr",
      {},
      columns.map((col) =>
        el("th", { style: col.style || "" }, col.label)
      )
    )
  );
  const body = el(
    "tbody",
    {},
    rows.map((cells, index) =>
      el(
        "tr",
        typeof cells.rowAttrs === "object" ? cells.rowAttrs : {},
        (cells.cells || cells).map((cell, col) =>
          el("td", { style: columns[col]?.cellStyle || "" }, cell)
        )
      )
    )
  );
  // .scroll-x wraps the table (not the frame) so narrow screens scroll it
  // horizontally without clipping the blueprint corner marks.
  const table = el("table", { class: "table" }, [head, body]);
  return blueprint({ style: wrapperStyle }, el("div", { class: "scroll-x" }, table));
}

// A dashed-frame empty state with a title, body and optional action button.
export function emptyState(title, body, actionNode, padding = "54px 24px") {
  return blueprint(
    { style: `padding: ${padding}; text-align: center; border-style: dashed` },
    [
      el("h4", { style: "margin-bottom: 4px" }, title),
      el(
        "p",
        { class: "text-muted", style: "font-size: 13px; max-width: 360px; margin: 0 auto 14px" },
        body
      ),
      actionNode || null,
    ]
  );
}
