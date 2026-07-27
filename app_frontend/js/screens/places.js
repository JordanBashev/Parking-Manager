// Places list — the home screen. Workers see their own open places; admins see
// all and can toggle Open/Archived. Rows link into the place detail. Includes the
// "New place" dialog that creates a place and jumps straight into entry.

import { api, ApiError } from "../api.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { contentColumn, dataTable, emptyState } from "../layout.js";
import { isAdmin } from "../state.js";
import { blueprint, closeDialog, el, fieldError, openDialog, primaryButton, toast } from "../ui.js";

let placeFilter = "open"; // admin-only toggle

function newPlaceDialog() {
  let name = "";
  const errorSlot = el("div");
  const input = el("input", {
    id: "np",
    class: "input",
    placeholder: "e.g. Central",
    onInput: (event) => (name = event.target.value),
    onKeydown: (event) => event.key === "Enter" && confirm(),
  });

  async function confirm() {
    if (!name.trim()) {
      errorSlot.replaceChildren(fieldError("Give the place a name."));
      return;
    }
    try {
      const place = await api.post("/places", { name: name.trim() });
      closeDialog();
      toast(`${place.name} created — start entering listings`);
      navigate(`/place/${place.id}`);
    } catch (error) {
      errorSlot.replaceChildren(fieldError("Could not create the place."));
    }
  }

  openDialog({
    title: "New place",
    body: "Worker and date are filled in automatically. You will land straight in the entry form.",
    bodyNodes: [el("div", { class: "field" }, [el("label", { for: "np" }, "Place name"), input, errorSlot])],
    confirmLabel: "Create & start entering",
    onConfirm: confirm,
  });
  setTimeout(() => input.focus(), 0);
}

export async function renderPlaces() {
  renderNav();
  const main = document.getElementById("main");
  const admin = isAdmin();
  const archived = admin && placeFilter === "archived";

  let places = [];
  try {
    places = await api.get(`/places?archived=${archived}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return navigate("/login");
    places = [];
  }

  const caption =
    (admin ? (archived ? "All archived places" : "All open places") : "Your open places") +
    ` · newest first · ${places.length} shown`;

  const header = el("div", { class: "screen-header", style: "display: flex; align-items: flex-end; gap: 16px; margin-bottom: 20px" }, [
    el("div", {}, [
      el("h2", { style: "margin: 0" }, "Places"),
      el("div", { style: "font-size: 12px; color: color-mix(in srgb, var(--color-text) 55%, transparent)" }, caption),
    ]),
    el("div", { class: "header-actions", style: "margin-left: auto; display: flex; align-items: center; gap: 12px" }, [
      admin ? filterToggle() : null,
      primaryButton("New place", newPlaceDialog),
    ]),
  ]);

  const columns = [
    { label: "Place", style: "width: 42%", cellStyle: "font-family: var(--font-heading); font-size: 16px" },
    { label: "Date", cellStyle: "font-variant-numeric: tabular-nums" },
    { label: "Worker" },
    { label: "Listings", cellStyle: "font-variant-numeric: tabular-nums" },
    { label: "Status", style: "text-align: right", cellStyle: "text-align: right" },
  ];

  let content;
  if (places.length === 0) {
    content = emptyState(
      archived ? "Nothing archived yet" : "No places yet",
      archived
        ? "Places appear here once a worker closes them at the end of the day."
        : "A place is one day's batch of work. Create one and start entering listings.",
      el("button", { class: "btn btn-secondary", onClick: newPlaceDialog }, "New place")
    );
  } else {
    const rows = places.map((place) => ({
      rowAttrs: {
        class: "row-link",
        style: place.archived ? "opacity: 0.62" : "",
        onClick: () => navigate(`/place/${place.id}`),
      },
      cells: [
        place.name,
        place.date,
        place.worker,
        String(place.listing_count ?? ""),
        el("span", { class: place.archived ? "tag tag-neutral" : "tag tag-outline" }, place.archived ? "Archived" : "Open"),
      ],
    }));
    content = dataTable(columns, rows);
  }

  main.replaceChildren(contentColumn([header, content]));
}

function filterToggle() {
  const make = (value, label) =>
    el("label", { class: "seg-opt" }, [
      el("input", {
        type: "radio",
        name: "pf",
        checked: placeFilter === value,
        onChange: () => {
          placeFilter = value;
          renderPlaces();
        },
      }),
      label,
    ]);
  return el("div", { class: "seg" }, [make("open", "Open"), make("archived", "Archived")]);
}
