// Hotels (admin) — the list that drives the pickers. Add, rename, and toggle
// active. Inactive is not deleted: it just stops being offered. Never a delete.

import { api, ApiError } from "../api.js";
import { contentColumn, dataTable } from "../layout.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { blueprint, el, primaryButton, toast } from "../ui.js";

export async function renderHotels() {
  renderNav();
  const main = document.getElementById("main");

  let hotels;
  try {
    hotels = await api.get("/hotels?active_only=false");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return navigate("/login");
    if (error instanceof ApiError && error.status === 403) return navigate("/");
    throw error;
  }

  let newName = "";
  const nameInput = el("input", {
    id: "h-new",
    class: "input",
    placeholder: "Hotel name",
    onInput: (e) => (newName = e.target.value),
    onKeydown: (e) => e.key === "Enter" && add(),
  });

  async function add() {
    if (!newName.trim()) return;
    try {
      await api.post("/hotels", { name: newName.trim() });
      toast(`${newName.trim()} added`);
      renderHotels();
    } catch (error) {
      toast(error instanceof ApiError && error.status === 409 ? "That hotel name already exists." : "Could not add the hotel.");
    }
  }

  const addRow = blueprint({ style: "padding: 14px; margin: 18px 0 22px; display: flex; gap: 10px; align-items: end" }, [
    el("div", { class: "field", style: "flex: 1" }, [el("label", { for: "h-new" }, "Add a hotel"), nameInput]),
    primaryButton("Add", add, { height: "36px" }),
  ]);

  const columns = [
    { label: "Name" },
    { label: "Status", style: "width: 120px" },
    { label: "Actions", style: "width: 190px; text-align: right", cellStyle: "text-align: right" },
  ];

  const rows = hotels.map((hotel) => ({
    rowAttrs: { style: hotel.active ? "" : "opacity: 0.6" },
    cells: [
      nameCell(hotel),
      el("span", { class: hotel.active ? "tag tag-accent" : "tag tag-neutral" }, hotel.active ? "Active" : "Inactive"),
      actionCell(hotel),
    ],
  }));

  main.replaceChildren(
    contentColumn([
      el("h2", { style: "margin: 0" }, "Hotels"),
      el("p", { class: "text-muted", style: "font-size: 13px; max-width: 520px" }, "These drive the listing pickers. Inactive is not deleted — an inactive hotel simply stops being offered; every existing listing still references it."),
      addRow,
      dataTable(columns, rows),
    ], 720)
  );
}

function nameCell(hotel) {
  const span = el("span", {}, hotel.name);
  return span;
}

function actionCell(hotel) {
  const container = el("div", { style: "display: flex; gap: 6px; justify-content: flex-end" });

  const rename = el("button", { class: "btn btn-ghost", style: "font-size: 12px", onClick: startRename }, "Rename");
  const toggle = el("button", {
    class: "btn btn-secondary",
    style: "font-size: 12px; padding: 2px 8px",
    onClick: async () => {
      try {
        await api.patch(`/hotels/${hotel.id}`, { active: !hotel.active });
        toast(hotel.active ? `${hotel.name} will no longer be offered in pickers` : `${hotel.name} is offered again`);
        renderHotels();
      } catch (error) {
        toast("Could not update the hotel.");
      }
    },
  }, hotel.active ? "Deactivate" : "Activate");

  function startRename() {
    let value = hotel.name;

    async function saveRename() {
      if (!value.trim()) return;
      try {
        await api.patch(`/hotels/${hotel.id}`, { name: value.trim() });
        toast("Hotel renamed");
        renderHotels();
      } catch (error) {
        toast(error instanceof ApiError && error.status === 409 ? "That hotel name already exists." : "Could not rename the hotel.");
      }
    }

    const input = el("input", {
      class: "input",
      value,
      autofocus: true,
      style: "min-height: 28px; padding: 2px 6px; max-width: 260px",
      onInput: (e) => (value = e.target.value),
      onKeydown: (e) => e.key === "Enter" && saveRename(),
    });
    // Replace the whole row's name cell: simplest is to rerender after save.
    container.replaceChildren(
      el("button", { class: "btn btn-ghost", style: "font-size: 12px", onClick: saveRename }, "Save"),
      el("button", { class: "btn btn-ghost", style: "font-size: 12px; color: var(--color-text)", onClick: renderHotels }, "Cancel"),
    );
    // Put the input in place of the name — find the name cell in the same row.
    const nameTd = container.closest("tr").firstChild;
    nameTd.replaceChildren(input);
    input.focus();
  }

  container.append(rename, toggle);
  return container;
}
