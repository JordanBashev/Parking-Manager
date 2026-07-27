// The single point that talks to the backend. Every call sends the session
// cookie (credentials: "include") and maps HTTP errors to a typed ApiError so
// screens can react to 401 / 403 / 404 / 409 / 422 without re-parsing responses.

import { API_BASE } from "./config.js";

export class ApiError extends Error {
  constructor(status, detail, fields) {
    super(detail || `Request failed (${status})`);
    this.status = status;
    this.detail = detail;
    this.fields = fields || null; // per-field messages from a 422
  }
}

function parseValidation(body) {
  // FastAPI 422: {detail: [{loc: [...,"field"], msg}, ...]} → {field: msg}.
  if (!Array.isArray(body?.detail)) return null;
  const fields = {};
  for (const item of body.detail) {
    const name = item.loc?.[item.loc.length - 1];
    if (name) fields[name] = item.msg;
  }
  return fields;
}

async function request(method, path, body) {
  const options = {
    method,
    credentials: "include",
    headers: {},
  };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(API_BASE + path, options);

  if (response.status === 204) return null;

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = typeof payload?.detail === "string" ? payload.detail : undefined;
    throw new ApiError(response.status, detail, parseValidation(payload));
  }
  return payload;
}

// Multipart POST (file upload). No Content-Type header — the browser sets it
// with the correct multipart boundary. Shares the same error mapping.
async function requestForm(path, formData) {
  const response = await fetch(API_BASE + path, {
    method: "POST",
    credentials: "include",
    body: formData,
  });
  if (response.status === 204) return null;
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof payload?.detail === "string" ? payload.detail : undefined;
    throw new ApiError(response.status, detail, parseValidation(payload));
  }
  return payload;
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  patch: (path, body) => request("PATCH", path, body),
  postForm: (path, formData) => requestForm(path, formData),
};

// Query-string builder that drops empty values (all report filters are optional).
export function query(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== "" && value !== null && value !== undefined) {
      search.set(key, value);
    }
  }
  const string = search.toString();
  return string ? `?${string}` : "";
}
