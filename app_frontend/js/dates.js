// Dates cross two boundaries: the API speaks dd/mm/yyyy, but native <input
// type="date"> only accepts/returns ISO yyyy-mm-dd. Convert at the edge.

export function displayToIso(display) {
  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec((display || "").trim());
  return match ? `${match[3]}-${match[2]}-${match[1]}` : "";
}

export function isoToDisplay(iso) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec((iso || "").trim());
  return match ? `${match[3]}/${match[2]}/${match[1]}` : "";
}
