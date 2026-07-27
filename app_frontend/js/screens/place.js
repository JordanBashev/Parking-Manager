// Place detail — the workhorse. Open places show the hotel-tile picker and the
// fast-entry form (Enter = save & next, hotel + end date persist across saves),
// plus the listings table with inline edit. Archived places show a read-only
// banner, no entry panel, no Edit affordance. Nothing is ever deleted.

import { api, ApiError } from "../api.js";
import { displayToIso, isoToDisplay } from "../dates.js";
import { contentColumn, emptyState } from "../layout.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { blueprint, closeDialog, el, fieldError, openDialog, primaryButton, toast } from "../ui.js";
import { scanStrip } from "../scan.js";

// 3-letter initials shown under a hotel name on its tile.
function hotelCode(name) {
  return name
    .replace(/[^A-Za-z ]/g, "")
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word[0])
    .join("")
    .slice(0, 3)
    .toUpperCase();
}

export async function renderPlace({ id }) {
  renderNav();
  const main = document.getElementById("main");

  let place;
  let hotels;
  try {
    [place, hotels] = await Promise.all([
      api.get(`/places/${id}`),
      api.get("/hotels?active_only=true"),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return navigate("/login");
    if (error instanceof ApiError && error.status === 404) {
      main.replaceChildren(
        contentColumn(emptyState("Not available", "That place is no longer visible to you.", backLink()))
      );
      return;
    }
    throw error;
  }

  const hotelName = (hotelId) => {
    const found = (place.listings_hotels || hotels).find((h) => h.id === hotelId);
    return found ? found.name : "—";
  };

  main.replaceChildren(
    contentColumn([
      backLink(),
      headerRow(place),
      place.archived ? archivedBanner(place) : null,
      place.archived ? null : entryPanel(place, hotels),
      listingsSection(place, hotels, hotelName),
    ])
  );
}

function backLink() {
  return el("a", { href: "/", "data-link": "", style: "font-size: 12px" }, "← All places");
}

function headerRow(place) {
  const meta = `${place.date} · ${place.worker} · ${place.listings.length} listings`;
  return el("div", { class: "screen-header", style: "display: flex; align-items: flex-end; gap: 14px; margin: 8px 0 20px" }, [
    el("h2", { style: "margin: 0" }, place.name),
    el("span", { class: place.archived ? "tag tag-neutral" : "tag tag-outline", style: "margin-bottom: 8px" }, place.archived ? "Archived" : "Open"),
    el("div", { class: "header-actions", style: "margin-left: auto; display: flex; align-items: center; gap: 18px" }, [
      el("div", { class: "num", style: "font-size: 12px; color: color-mix(in srgb, var(--color-text) 55%, transparent)" }, meta),
      place.archived ? null : el("button", { class: "btn btn-secondary", style: "color: var(--color-accent-800)", onClick: () => askArchive(place) }, "Archive this place"),
    ]),
  ]);
}

function archivedBanner(place) {
  return blueprint(
    { style: "padding: 12px 14px; margin-bottom: 20px; background: var(--color-accent-100); display: flex; gap: 10px; align-items: baseline" },
    [
      el("div", { style: "font-family: var(--font-heading); font-size: 15px; color: var(--color-accent-900)" }, `Archived on ${place.archived_at || ""}`),
      el("div", { style: "font-size: 12px; color: var(--color-accent-800)" }, "Read-only. Archiving is permanent — listings can be viewed but not changed."),
    ]
  );
}

function askArchive(place) {
  openDialog({
    title: "Archive this place?",
    body: "Archiving is permanent — the place becomes read-only and can never be reopened or deleted.",
    confirmLabel: "Archive permanently",
    onConfirm: async () => {
      try {
        await api.post(`/places/${place.id}/archive`);
        closeDialog();
        toast("Place archived — now read-only");
        renderPlace({ id: place.id });
      } catch (error) {
        closeDialog();
        toast("Could not archive the place.");
      }
    },
  });
}

// --- entry panel -----------------------------------------------------------

function entryPanel(place, hotels) {
  // Draft persists hotel + end date across saves (they repeat across entries).
  const draft = { hotel_id: null, model: "", reg_number: "", end_date: "", count: "", price: "" };
  const errorSlots = {};
  const panel = blueprint({ style: "padding: 18px; margin-bottom: 26px" }, []);

  function slot(name) {
    if (!errorSlots[name]) errorSlots[name] = el("div");
    return errorSlots[name];
  }

  const tileGrid = el("div", {
    class: "tile-grid",
    style: "display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; margin-bottom: 18px",
  });

  function paintTiles() {
    tileGrid.replaceChildren(
      ...hotels.map((hotel) => {
        const selected = draft.hotel_id === hotel.id;
        const style = [
          "display: flex; flex-direction: column; align-items: flex-start; gap: 2px; text-align: left",
          "padding: 10px 12px; cursor: pointer; border-radius: 0; font-family: var(--font-body)",
          selected
            ? "background: var(--color-accent); color: var(--color-bg); border: 1px solid var(--color-accent); box-shadow: var(--shadow-sm)"
            : "background: transparent; color: var(--color-text); border: 1px solid var(--color-divider)",
        ].join("; ");
        return el("button", {
          class: "tile",
          style,
          onClick: () => {
            draft.hotel_id = hotel.id;
            slot("hotel").replaceChildren();
            paintTiles();
          },
        }, [
          el("span", { style: "font-family: var(--font-heading); font-size: 16px; line-height: 1.15" }, hotel.name),
          el("span", { style: "font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.55" }, hotelCode(hotel.name)),
        ]);
      })
    );
  }
  paintTiles();

  const modelInput = textField("Model *", "e.g. Alto 4-door", (v) => (draft.model = v), slot("model"));
  const regInput = textField("Registration no. *", "AB 12 3456", (v) => (draft.reg_number = v), slot("reg_number"), true);
  const endInput = el("input", { class: "input num", type: "date", onInput: (e) => (draft.end_date = isoToDisplay(e.target.value)) });
  const countInput = el("input", { class: "input num", placeholder: "—", onInput: (e) => (draft.count = e.target.value) });
  const priceInput = el("input", { class: "input num", placeholder: "0.00", onInput: (e) => (draft.price = e.target.value) });

  const saveButton = primaryButton("Save & next", save, { height: "36px", minWidth: "132px" });

  function fieldWrap(labelText, input, errorSlot) {
    return el("div", { class: "field" }, [el("label", {}, labelText), input, errorSlot || null]);
  }

  const grid = el("div", { class: "grid-2col-mobile", style: "display: grid; grid-template-columns: 1.2fr 1.2fr 1fr 0.7fr 0.9fr auto; gap: 12px; align-items: end" }, [
    modelInput.wrap,
    regInput.wrap,
    fieldWrap("End date *", endInput, slot("end_date")),
    fieldWrap("Count", countInput),
    fieldWrap("Price", priceInput),
    saveButton,
  ]);

  // Enter anywhere in the form submits.
  grid.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      save();
    }
  });

  async function save() {
    Object.values(errorSlots).forEach((s) => s.replaceChildren());
    const errors = {};
    if (!draft.hotel_id) errors.hotel = "Pick a hotel.";
    if (!draft.model.trim()) errors.model = "Model is required.";
    if (!draft.reg_number.trim()) errors.reg_number = "Registration number is required.";
    if (!draft.end_date.trim()) errors.end_date = "End date is required.";
    if (Object.keys(errors).length) {
      for (const [name, message] of Object.entries(errors)) slot(name).replaceChildren(fieldError(message));
      return;
    }

    saveButton.lastChild.textContent = "Saving…";
    const body = {
      hotel_id: draft.hotel_id,
      model: draft.model.trim(),
      reg_number: draft.reg_number.trim(),
      end_date: draft.end_date,
    };
    if (draft.count !== "") body.count = Number(draft.count);
    if (draft.price !== "") body.price = draft.price;

    try {
      await api.post(`/places/${place.id}/listings`, body);
      toast("Listing saved — form ready for the next one");
      navigate(`/place/${place.id}`); // re-render appends the new row; hotel/date persist below
    } catch (error) {
      saveButton.lastChild.textContent = "Save & next";
      if (error instanceof ApiError && error.status === 409) {
        toast("This place is archived and read-only.");
      } else if (error instanceof ApiError && error.fields) {
        for (const [name, message] of Object.entries(error.fields)) slot(name)?.replaceChildren(fieldError(message));
      } else {
        toast("Could not save the listing.");
      }
    }
  }

  // Scan strip sits between the hotel tiles and the field grid. It repaints
  // (empty ↔ filled styling) whenever the reg field changes.
  const stripHost = el("div");
  function paintStrip() {
    stripHost.replaceChildren(
      scanStrip(
        () => draft.reg_number,
        (regNumber) => {
          draft.reg_number = regNumber;
          regInput.input.value = regNumber;
          slot("reg_number").replaceChildren(); // clear any reg validation error
          paintStrip();
          regInput.input.focus();
        }
      )
    );
  }
  paintStrip();
  // Typing in the reg field also flips the strip between its two states.
  regInput.input.addEventListener("input", paintStrip);

  panel.append(
    el("div", { style: "display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px" }, [
      el("h6", { style: "margin: 0" }, "New listing"),
      el("div", { style: "font-size: 11px; color: color-mix(in srgb, var(--color-text) 50%, transparent)" }, "Enter saves and clears the form"),
    ]),
    el("div", { style: "font-size: 12px; color: color-mix(in srgb, var(--color-text) 70%, transparent); margin-bottom: 6px" }, "Hotel"),
    tileGrid,
    slot("hotel"),
    stripHost,
    grid
  );
  return panel;
}

function textField(label, placeholder, onChange, errorSlot, numeric) {
  const input = el("input", { class: numeric ? "input num" : "input", placeholder, onInput: (e) => onChange(e.target.value) });
  const wrap = el("div", { class: "field" }, [el("label", {}, label), input, errorSlot || null]);
  return { input, wrap };
}

// --- listings table --------------------------------------------------------

function listingsSection(place, hotels, hotelName) {
  const heading = el("div", { style: "display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px" }, [
    el("h6", { style: "margin: 0" }, "Listings in this place"),
    el("div", { style: "font-size: 11px; color: color-mix(in srgb, var(--color-text) 50%, transparent)" }, "Oldest first · nothing is ever deleted, only corrected"),
  ]);

  if (place.listings.length === 0) {
    return el("div", {}, [heading, emptyState("No listings yet", "Pick a hotel above and start typing — saved listings appear here.", null, "40px 24px")]);
  }

  const listingsTable = el("table", { class: "table", style: place.archived ? "opacity: 0.72" : "" }, [
    el("thead", {}, el("tr", {}, [
      el("th", { style: "width: 34px" }, "#"),
      el("th", {}, "Hotel"), el("th", {}, "Model"), el("th", {}, "Reg no."), el("th", {}, "End date"),
      el("th", { style: "text-align: right" }, "Count"), el("th", { style: "text-align: right" }, "Price"),
      el("th", { style: "width: 74px" }, ""),
    ])),
    el("tbody", {}, place.listings.map((listing, index) => listingRow(place, hotels, hotelName, listing, index))),
  ]);

  return el("div", {}, [
    heading,
    blueprint({ style: "padding: 4px 14px 8px" }, el("div", { class: "scroll-x" }, listingsTable)),
  ]);
}

function listingRow(place, hotels, hotelName, listing, index) {
  const row = el("tr", {});

  function renderRead() {
    row.replaceChildren(
      el("td", { class: "num text-muted" }, String(index + 1)),
      el("td", {}, hotelName(listing.hotel_id)),
      el("td", {}, listing.model),
      el("td", { class: "num" }, listing.reg_number),
      el("td", { class: "num" }, listing.end_date),
      el("td", { class: "num", style: "text-align: right" }, listing.count == null ? "—" : String(listing.count)),
      el("td", { class: "num", style: "text-align: right" }, listing.price == null ? "—" : listing.price),
      el("td", { style: "text-align: right" }, place.archived ? "" : el("button", { class: "btn btn-ghost", style: "font-size: 12px", onClick: renderEdit }, "Edit")),
    );
  }

  function renderEdit() {
    const draft = {
      hotel_id: listing.hotel_id,
      model: listing.model,
      reg_number: listing.reg_number,
      end_date: listing.end_date,
      count: listing.count == null ? "" : String(listing.count),
      price: listing.price == null ? "" : listing.price,
    };
    const small = { minHeight: "28px", padding: "2px 6px" };

    // If the current hotel is inactive it won't be in the active list; keep it as a
    // labelled option so the row can still be saved.
    const options = hotels.slice();
    if (!options.some((h) => h.id === listing.hotel_id)) {
      options.push({ id: listing.hotel_id, name: `${hotelName(listing.hotel_id)} (inactive)` });
    }
    const hotelSelect = el("select", { class: "input", style: small, onChange: (e) => (draft.hotel_id = e.target.value) },
      options.map((h) => el("option", { value: h.id, selected: h.id === listing.hotel_id }, h.name)));

    const modelInput = el("input", { class: "input num", style: small, value: draft.model, onInput: (e) => (draft.model = e.target.value) });
    const regInput = el("input", { class: "input num", style: small, value: draft.reg_number, onInput: (e) => (draft.reg_number = e.target.value) });
    const endInput = el("input", { class: "input num", type: "date", style: small, value: displayToIso(draft.end_date), onInput: (e) => (draft.end_date = isoToDisplay(e.target.value)) });
    const countInput = el("input", { class: "input num", style: small, value: draft.count, onInput: (e) => (draft.count = e.target.value) });
    const priceInput = el("input", { class: "input num", style: small, value: draft.price, onInput: (e) => (draft.price = e.target.value) });

    async function saveEdit() {
      const body = {
        hotel_id: draft.hotel_id,
        model: draft.model.trim(),
        reg_number: draft.reg_number.trim(),
        end_date: draft.end_date,
        count: draft.count === "" ? null : Number(draft.count),
        price: draft.price === "" ? null : draft.price,
      };
      try {
        const updated = await api.patch(`/listings/${listing.id}`, body);
        Object.assign(listing, updated);
        renderRead();
        toast("Listing corrected");
      } catch (error) {
        if (error instanceof ApiError && error.status === 409) toast("This place is archived and read-only.");
        else toast("Could not save the correction.");
      }
    }

    row.replaceChildren(
      el("td", { class: "num text-muted" }, String(index + 1)),
      el("td", {}, hotelSelect),
      el("td", {}, modelInput),
      el("td", {}, regInput),
      el("td", {}, endInput),
      el("td", { style: "text-align: right" }, countInput),
      el("td", { style: "text-align: right" }, priceInput),
      el("td", { style: "text-align: right" }, el("div", { style: "display: flex; gap: 4px; justify-content: flex-end" }, [
        el("button", { class: "btn btn-ghost", style: "font-size: 12px", onClick: saveEdit }, "Save"),
        el("button", { class: "btn btn-ghost", style: "font-size: 12px; color: var(--color-text)", onClick: renderRead }, "Cancel"),
      ])),
    );
  }

  renderRead();
  return row;
}
