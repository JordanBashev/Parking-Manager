// Reports (admin) — filters over archived data (combined with AND), headline
// stats, and per-hotel / per-worker breakdowns. Results recompute only on Apply.

import { api, ApiError, query } from "../api.js";
import { displayToIso, isoToDisplay } from "../dates.js";
import { contentColumn, dataTable } from "../layout.js";
import { renderNav } from "../nav.js";
import { navigate } from "../router.js";
import { blueprint, el, primaryButton, toast } from "../ui.js";

export async function renderReports() {
  renderNav();
  const main = document.getElementById("main");

  // Reference data for the filter selects, plus an initial unfiltered report.
  let hotels, workers, report;
  try {
    [hotels, report] = await Promise.all([
      api.get("/hotels?active_only=false"),
      api.get("/admin/reports"),
    ]);
    const users = await api.get("/users");
    workers = users.filter((u) => u.role === "worker").map((u) => u.first_name);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return navigate("/login");
    if (error instanceof ApiError && error.status === 403) return navigate("/");
    throw error;
  }

  const filters = { date_from: "", date_to: "", hotel_id: "", worker: "" };

  const resultsSlot = el("div");
  paintResults(resultsSlot, report);

  const fromInput = el("input", { class: "input num", type: "date", onInput: (e) => (filters.date_from = isoToDisplay(e.target.value)) });
  const toInput = el("input", { class: "input num", type: "date", onInput: (e) => (filters.date_to = isoToDisplay(e.target.value)) });
  const hotelSelect = el("select", { class: "input", onChange: (e) => (filters.hotel_id = e.target.value) },
    [el("option", { value: "" }, "All hotels"), ...hotels.map((h) => el("option", { value: h.id }, h.name))]);
  const workerSelect = el("select", { class: "input", onChange: (e) => (filters.worker = e.target.value) },
    [el("option", { value: "" }, "All workers"), ...workers.map((w) => el("option", { value: w }, w))]);

  const applyButton = primaryButton("Apply", apply, { height: "36px", minWidth: "96px" });

  async function apply() {
    applyButton.lastChild.textContent = "Loading…";
    try {
      const fresh = await api.get(`/admin/reports${query(filters)}`);
      paintResults(resultsSlot, fresh);
    } catch (error) {
      toast("Could not load the report.");
    } finally {
      applyButton.lastChild.textContent = "Apply";
    }
  }

  function clear() {
    filters.date_from = filters.date_to = filters.hotel_id = filters.worker = "";
    fromInput.value = toInput.value = "";
    hotelSelect.value = workerSelect.value = "";
    apply();
  }

  const filterBar = blueprint({ class: "grid-2col-mobile", style: "padding: 14px; margin: 18px 0 22px; display: grid; grid-template-columns: 150px 150px 1fr 1fr auto auto; gap: 12px; align-items: end" }, [
    el("div", { class: "field" }, [el("label", {}, "From"), fromInput]),
    el("div", { class: "field" }, [el("label", {}, "To"), toInput]),
    el("div", { class: "field" }, [el("label", {}, "Hotel"), hotelSelect]),
    el("div", { class: "field" }, [el("label", {}, "Worker"), workerSelect]),
    el("button", { class: "btn btn-secondary", style: "height: 36px", onClick: clear }, "Clear"),
    applyButton,
  ]);

  main.replaceChildren(
    contentColumn([
      el("h2", { style: "margin: 0" }, "Reports"),
      el("p", { class: "text-muted", style: "font-size: 13px" }, "Archived work only. Filters combine."),
      filterBar,
      resultsSlot,
    ])
  );
}

function statCard(label, value, note) {
  return blueprint({ class: "card", style: "padding: 16px 18px; gap: 2px" }, [
    el("div", { class: "card-kicker" }, label),
    el("div", { class: "num", style: "font-family: var(--font-heading); font-size: 40px; line-height: 1.05" }, value),
    el("div", { style: "font-size: 11px; color: color-mix(in srgb, var(--color-text) 50%, transparent)" }, note),
  ]);
}

function paintResults(slot, report) {
  const empty = report.total_listings === 0;

  const stats = el("div", { style: "display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 26px" }, [
    statCard("Listings", String(report.total_listings), "in the current filter"),
    statCard("Total count", String(report.total_count), "sum of the count column"),
    statCard("Total price", report.total_price, "sum of the price column"),
  ]);

  const hotelColumns = [
    { label: "Hotel" },
    { label: "Entered", style: "width: 96px", cellStyle: "font-variant-numeric: tabular-nums; color: color-mix(in srgb, var(--color-text) 55%, transparent)" },
    { label: "Listings", style: "text-align: right", cellStyle: "text-align: right" },
    { label: "Count", style: "text-align: right", cellStyle: "text-align: right" },
    { label: "Price", style: "text-align: right", cellStyle: "text-align: right" },
  ];
  const hotelRows = report.by_hotel.map((row) => [row.hotel_name, row.entered_date, String(row.total_listings), String(row.total_count), row.total_price]);

  const workerColumns = [
    { label: "Worker" },
    { label: "Listings", style: "text-align: right", cellStyle: "text-align: right" },
    { label: "Count", style: "text-align: right", cellStyle: "text-align: right" },
    { label: "Price", style: "text-align: right", cellStyle: "text-align: right" },
  ];
  const workerRows = report.by_worker.map((row) => [row.worker, String(row.total_listings), String(row.total_count), row.total_price]);

  const emptyLine = () => el("div", { class: "text-muted", style: "padding: 26px 0; text-align: center; font-size: 13px" }, "No results for this filter.");

  const breakdowns = el("div", { class: "grid-stack-mobile", style: "display: grid; grid-template-columns: 1fr 1fr; gap: 22px" }, [
    el("div", {}, [el("h6", {}, "Per hotel · by date entered"), empty ? blueprint({ style: "padding: 4px 14px 8px" }, emptyLine()) : dataTable(hotelColumns, hotelRows)]),
    el("div", {}, [el("h6", {}, "Per worker"), empty ? blueprint({ style: "padding: 4px 14px 8px" }, emptyLine()) : dataTable(workerColumns, workerRows)]),
  ]);

  slot.replaceChildren(stats, breakdowns);
}
