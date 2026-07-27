# CLAUDE.md — Management System (FastAPI)

## Project
A simple, straightforward management system for tracking **places** and their
**listings** (e.g. hotel-related entries). Built in **Python** with **FastAPI**,
**SQLAlchemy (async)** over **SQLite (aiosqlite)**. Auth is **session-cookie** based
with a simple **admin / non-admin** role system.

**Frontend is intentionally minimal and not a focus:** plain static **HTML + vanilla
JS** (`fetch`) talking to JSON endpoints. **No templating engine (no Jinja), no JS
framework, no build step.** Keep it dead simple; effort goes into the backend.

I will tell you what to build in the moment.
Keep this file accurate: maintain a **CURRENT LOGIC** section (data model, routes,
auth flow, page flow) so the code is understood, not assumed. IF you would have to
assume something, ASK before proceeding. Fill in the **ROADMAP** with whole subjects
we complete (not every step — e.g. "auth & roles", not each endpoint). Add new
**conventions** only after discussing them with me first — never on your own.

When describing something to set up (a route, a table, a page), cover it fully and
understandably: what it is, what it depends on, and what it connects to. Do not
introduce a piece without explaining what it needs and how it fits.

## Stack
- **Python 3.12+**, **FastAPI** (newest stable). Target current FastAPI APIs.
- **SQLAlchemy 2.x async** ORM + **aiosqlite** driver. All DB access is `async`.
- **SQLite** for now (single-file DB). Structured so a move to Postgres later is easy.
- **Pydantic v2** for request/response schemas and validation.
- **Frontend:** static `.html` + vanilla `.js` served by FastAPI; `fetch` calls the
  JSON API. No Jinja, no framework, no bundler.
- **Passwords hashed** (argon2 or bcrypt via passlib). Never store plaintext.
- Never switch major versions silently. Before adopting a newer major, tell me what
  changed and why upgrading is worth it.

## How we work
- **Code is written directly into the project** (plain `.py`, `.html`, `.js` — all
  diff cleanly under git). Keep it that way.
- **Migrations:** schema changes go through a clear, reviewable path (Alembic once the
  schema stabilises; until then, document schema changes explicitly). Never silently
  drop/recreate tables with real data.
- **Secrets** (session secret, admin bootstrap) come from environment / a `.env` that
  is git-ignored.
- The project is under **git**. DO NOT DO ANYTHING WITH GIT UNLESS SPECIFICALLY ASKED TO!!!

## Coding rules (follow strictly)
1. When introducing a system, first explain step by step which **built-in** framework
   features it uses (FastAPI dependencies, SQLAlchemy sessions, Pydantic models, etc.).
2. State which files will be created, their names, and what goes in each — and explain how
   each works IF the file is something specific and needed. explanation is nesseccery only when the file name itself doesn't explain whats inside of it.
3. Write short, readable, self-explanatory code with precise naming and clear
   structure. Use the right construct for the job: comprehension over manual loop when
   clearer, `match` instead of long if/elif chains, early returns over deep nesting,
   etc. Apply the same discipline to file and module organization.
4. Explain in detail **how** and **why** the code works ONLY WHERE NESSECCERY AND IS A MUST ELSE DON'T.
5. Use the cleanest approach available. If something looks odd, explain why it is
   written that way.
6. Use an appropriate **design pattern** and explain it.
7. Don't scatter comments. Comment only where the code can't speak for itself —
   well-named code needs few comments. Public functions get a short docstring.
8. Prefer the **newest stable versions**. Periodically check for updates and tell me
   whether to upgrade and why. Never switch versions silently.
9. **Optimize** reasonably: avoid N+1 queries (use joins/`selectinload`), index columns
   you filter on, don't load whole tables to count. Point out wins and explain the gain.
10. Always ask with a code **preview** before writing non-trivial code — confirm it's
    good first.
11. No single-letter names for variables / lists / classes / etc. Names must be
    meaningful and understandable. Don't over-qualify either: a `price` inside a
    `Listing` needn't be `listing_price` — context already makes it clear.
12. If something is global / used across many scopes, put it in a dedicated module at
    the top of *that scope only* (e.g. shared `config.py`, `constants.py`). Out-of-scope
    code must not depend on it. Keep unrelated areas from knowing about each other.
13. No magic strings/numbers. ALWAYS name values (`MAX_PAGE_SIZE = 50`,
    `Role.ADMIN = "admin"`). Exceptions: 0, 1, True, False and the obvious. Values like
    `-63` or a bare `"admin"` sprinkled around are NOT acceptable — define them once.
14. Every request/response field (Pydantic) and every non-obvious model column gets a
    short description of **what it is and how it's used** (via Pydantic `Field(...,
    description=...)` and a comment on the column). The point is that months later each
    field is self-explanatory in the code and the auto-generated `/docs`.
15. **Group related inputs into an object/class, don't pass loose parameters.** If a
    function takes **more than two** arguments, OR takes two that aren't obvious on
    first read, bundle them into a named class (a Pydantic model or a small dataclass)
    that describes the input as a whole — e.g. `ReportFilters` instead of
    `(date_from, date_to, hotel_id, worker)`. The class name states intent, each field
    is documented once, and adding an input doesn't reshuffle every call site. Two
    clearly-named arguments (`get(place_id, user)`) stay as they are.

## Conventions
- File & module names: `snake_case.py`. Class names: `PascalCase`. Constants:
  `UPPER_SNAKE`.
- **Every package folder has an `__init__.py`** — the app root and every sub-scope.
- **The main application file is `app/main.py`.** Never renamed.
- **Layered structure over god-modules:** keep concerns separated into small,
  single-responsibility modules. Split early so areas stay independent as the project
  grows. The layers, and the strict rules between them:
  - **routers/** — HTTP only: read the request, call **one service**, return a schema.
    A router contains **no business logic and no DB access**, ever.
  - **services/** — business logic. **A service MUST have a repository.** No service
    exists without one, and a service never issues a query itself.
  - **repositories/** — the *only* place SQLAlchemy queries live. Take an
    `AsyncSession`, return ORM objects. Know nothing about HTTP or Pydantic.
  - **db/** — engine, session factory, `base.py`, and **`db/models/`** (ORM models
    live inside `db`, not at the app root).
  - **schemas/** — Pydantic request/response models. Top-level, outside `db`.
  - **dependencies/** — **all** `Depends(...)` providers live here (DB session,
    current user, role guards). Nothing else defines a dependency provider.
- **Dependency injection** is the core FastAPI pattern: DB sessions, current user, and
  role checks are provided via `Depends(...)` from `app/dependencies/` — not fetched
  ad-hoc inside handlers.
- **Async all the way down:** DB calls, request handlers, and anything I/O-bound are
  `async`; never block the event loop with sync DB/network calls.
- **UUID primary keys** (uuid4) for all main tables, as specified.
- **Timestamps:** store timezone-aware UTC; `created`/`date` fields are set server-side
  at creation, never trusted from the client.
- Validation lives in **Pydantic schemas**; the DB layer assumes already-valid data.

## Data model (CURRENT LOGIC — keep in sync with code)

### User
- `id` — uuid4, PK
- `username` — unique
- `first_name` — used to auto-fill a place's "worker"
- `password_hash`
- `role` — `admin` | `worker` (non-admin)
- `created` — creation timestamp

### Place
- `id` — uuid4, PK
- `name` — e.g. "Central"
- `date` — creation date (server-set)
- `worker` — the creating user's first name (from `User.first_name`)
- `created_by` — FK → User.id (owner)
- `archived` — bool; archived places are read-only, admin-only
- `archived_at` — timestamp when archived (nullable)
- **has many** Listings

### Listing (belongs to a Place)
- `id` — uuid4, PK
- `place_id` — FK → Place.id
- `hotel_id` — FK → Hotel.id (referenced by id, not name)
- `model` — string
- `reg_number` — string (registration number)
- `date` — creation date (server-set)
- `end_date` — user-selected end date
- `count` — numeric (meaning TBD — kept flexible/nullable, refined later)
- `price` — numeric (meaning TBD — kept flexible/nullable, refined later)

### Hotel (the `hotel_names` list)
- `id` — uuid4, PK
- `name` — string, admin-managed, **unique + indexed**
- `active` — bool; **hotels are never deleted.** Listings reference them forever, so
  deactivating only removes the hotel from the selection boxes and preserves history.
- Drives the clickable hotel boxes when adding a listing.

### Conventions this model layer establishes
- **Money is `Decimal`, never `float`** — `Numeric(PRICE_TOTAL_DIGITS,
  PRICE_DECIMAL_PLACES)` = 2 decimal places, 8 digits before the point. Binary floats
  cannot represent 0.10 exactly and totals drift.
- **Dates: `dd/mm/yyyy` at the API edge, real SQL `Date` in the DB.** The conversion is
  defined once in `app/schemas/fields.py` as the `DisplayDate` annotated type
  (`BeforeValidator` parses, `PlainSerializer` formats). Storing text dates would break
  sorting and range queries. ISO input is deliberately rejected — one format only, so
  `01/12` is never ambiguous.
- **Indexes** on every column that gets filtered: `Place.created_by`, `Place.archived`,
  `Listing.place_id`, `Listing.hotel_id`, `Listing.reg_number`, `Listing.date`,
  `Hotel.active`.
- **`Place.listings` cascades** (`all, delete-orphan`) so deleting a place leaves no
  orphan listings.
- **`Place.worker` is a deliberate snapshot** of the creator's first name, not a join —
  renaming a user must not rewrite history on their past places.

### Place routes & rules
- `POST  /api/places` — create. Accepts **only `name`**; `worker`, `date` and
  `created_by` are set server-side from the session and ignored if a client sends them.
- `GET   /api/places` — own places (admin: all), newest first.
  `?archived=true` is admin-only and returns `[]` for a worker.
- `GET   /api/places/{id}` — one place **with its listings** (`selectinload`, no N+1).
- `PATCH /api/places/{id}` — rename; 409 once archived.
- `POST  /api/places/{id}/archive` — the archive button; sets `archived_at`.
- `POST  /api/places/archive-all` — **admin-only, testing/ops**: runs end-of-day
  archiving now (same action as the scheduler), returns `{archived: N}`. Declared
  before `/{id}/archive`; no route clash (literal path, different method from
  `GET /{id}`).

**Auto end-of-day archiving.** `app/scheduler.py` builds an APScheduler
`AsyncIOScheduler` started/stopped in the lifespan. A daily `CronTrigger` at
**midnight GMT** (`ARCHIVE_*` constants) calls `PlaceService.archive_all_open()`,
which the manual button also calls — one code path. The job runs outside any request,
so it builds its own session + service (no `Depends`). `archive_all_open` is a single
`UPDATE ... WHERE archived = false` (no row loading) and is unscoped by owner because
it is a system action, not a user action; already-archived places are skipped.
- **There is no delete route. Places are NEVER deleted, and archiving is terminal —
  there is no un-archive.** Archived means "that date is done".

**Ownership scoping is structural, not a check.** `PlaceRepository` has no unscoped
query method: every read takes `owner_id`, where `None` (admin) means unrestricted.
A caller therefore cannot forget to scope a query. `PlaceService._owner_filter` is the
single place the role decides that value.

**404 vs 409, deliberately:**
- A worker gets **404** for another worker's place *and* for their own archived place —
  403 would confirm the place exists and leak its existence.
- An **admin** writing to an archived place gets **409** (visible, but read-only).
- So re-archiving is 404 for the worker who archived it, 409 for an admin.

### Admin report routes & rules
- `GET /api/admin/reports` — admin-only. Filters (`date_from`, `date_to`, `hotel_id`,
  `worker`) are optional and **combine with AND**; they bind from the query string into
  the `ReportFilters` model via `Depends()`.
- **Reports cover archived places only** — always, not a toggle. Open places are still
  being edited, so they never appear in a report.
- **Date range is inclusive of both endpoints.** `Listing.date` is a timestamp, so the
  upper bound compares `< date_to + 1 day` (`ReportFilters.date_to_exclusive`) — an
  entry at 23:59 on the last day is included.
- Returns totals (`total_listings`, `total_count`, `total_price`) plus the same three
  grouped `by_hotel` and `by_worker`, highest price first.
- **`by_hotel` is grouped by hotel AND entry date** (`func.date(Listing.date)`): one
  hotel with listings on several days yields one row per day, each carrying
  `entered_date` (dd/mm/yyyy). Frontend titles it "Per hotel · by date entered".
- **All aggregation is in SQL** (`func.count` / `func.sum`, grouped) — rows are never
  loaded into Python to count. `SUM` over no rows is coalesced to 0 / 0.00.
- `Listing.date` is **indexed** for the range filter.

### Listing routes & rules
- `POST  /api/places/{place_id}/listings` — the fast-entry save.
- `GET   /api/places/{place_id}/listings` — a place's listings, oldest first.
- `PATCH /api/listings/{id}` — correct a listing while its place is open.
- **No DELETE route.** A mistyped listing is *edited*, never deleted.
- On create: `end_date` is **required**, `count`/`price` optional (fill in later),
  `place_id` comes from the URL and `date` is server-set.
- `hotel_id` must reference an **existing, active** hotel → 422 otherwise.
- `PATCH` uses `exclude_unset`, so omitting a field leaves it untouched while
  sending `null` explicitly clears it.

**Listings have no permissions of their own.** `ListingService` composes
`PlaceService` and `HotelService` and resolves the parent place through
`PlaceService` on every operation, so the ownership/archived rules are defined once
instead of duplicated. This is why a listing on another worker's place is 404, and
why writing to an archived place is 404 for a worker but 409 for an admin.

### Hotel routes
- `GET   /api/hotels` — any signed-in user; `?active_only=true` (default) for the boxes.
- `POST  /api/hotels` — admin-only; 409 if the name exists.
- `PATCH /api/hotels/{id}` — admin-only; rename and/or set `active`. 404 / 409.

## Auth & roles
- **Session cookies**: login sets an HTTP-only cookie holding the user id, signed with
  `itsdangerous.URLSafeTimedSerializer` (signed, *not* encrypted) using
  `SESSION_SECRET`. Expires after **7 days** (`SESSION_MAX_AGE_SECONDS`).
- **Deny by default.** `RequireSessionMiddleware` (`app/middleware.py`) rejects every
  request with 401 unless its path is in `PUBLIC_PATHS` (login, health, docs) or under
  `/static`. The middleware only validates the cookie's signature; loading the user and
  checking their role stays in `current_user` / `require_admin`.
  **Why middleware and not `FastAPI(dependencies=[...])`:** FastAPI *concatenates*
  app/router/route dependency lists — it never replaces them — so `dependencies=[]` on
  `include_router` cannot exempt the login route. That approach locks everyone out.
- **401 vs 403:** 401 = no/invalid session. 403 = valid session, insufficient role.
  The API never redirects; the frontend decides what to do with a 401.
- **Standalone frontend ⇒ cross-origin cookie.** Because `app_frontend/` is served on
  its own origin, the session cookie is `SameSite=none` (`COOKIE_SAMESITE`) so the
  browser sends it cross-site. **`COOKIE_SECURE=true` is required even in dev:** a
  `SameSite=None` cookie without `Secure` is silently dropped by the browser — there is
  NO localhost exemption for that rule (the localhost exemption is only for Secure's
  HTTPS requirement). Symptom of getting this wrong: login returns 200 but the next
  request is 401 because the cookie was never stored. `http://localhost` is a secure
  context, so `Secure` cookies work over it. CORS (`CORSMiddleware`,
  `allow_credentials`, origin = `FRONTEND_ORIGIN`) is added **after**
  `RequireSessionMiddleware` so it runs first and answers the preflight `OPTIONS`
  before auth can reject it. `logout` must clear the cookie with the same
  `samesite`/`secure` attributes it was set with. Also: the browser URL must match
  `FRONTEND_ORIGIN` exactly — `localhost` and `127.0.0.1` are different origins to CORS
  (a mismatch shows as 400 on the `OPTIONS` preflight).
- **No open registration.** `POST /api/users` is admin-only and creates **workers only**
  — admins are made *exclusively* by `seed_admin.py`.
- Passwords hashed with **bcrypt directly** (no passlib), capped at 72 characters.
- Roles: `admin` (full access, archives, queries) and `worker` (own places/listings).

### Auth routes
- `POST /api/auth/login` — public; sets the session cookie, returns `UserRead`.
- `POST /api/auth/logout` — clears the cookie, 204.
- `GET  /api/auth/me` — the signed-in account.
- `POST /api/users` — admin-only, creates a worker; 409 if the username is taken.
- `GET  /api/users` — admin-only, lists all accounts.

## Page / usage flow
1. Admin creates a user account and hands over the credentials.
2. User logs in.
3. **Create a Place:** user names it (e.g. "Central"); `worker` auto-fills from their
   first name and `date` from now. On creation, the **add-listings page opens
   automatically** for fast entry.
4. **Add listings:** pick a **hotel** from clickable boxes (from the Hotel table) →
   enter `reg_number`, `model`, `end_date`, `price`, `count` → save. Repeat quickly.
5. A **worker sees only their own** places/listings; **admins see everything**.
6. **Archiving:** a place can be **archived manually** (button) when its day is done;
   archived places become **admin-only, read-only**. (Auto end-of-day archiving is a
   later addition — see roadmap.)
7. **Admin queries** over archived data: counts and money totals over date ranges, and
   other inquiries.

## Roadmap
- [x] Project scaffold (FastAPI app, async SQLAlchemy + SQLite, config, layered
  package structure, `/api/health`, static mount). Tables are created by
  `Base.metadata.create_all` in lifespan; **Alembic comes later**.
- [x] Auth & roles (signed session-cookie login, deny-by-default middleware,
  admin/worker guards, `seed_admin.py` CLI, login page)
- [x] Data model (User, Place, Listing, Hotel ORM models + full Hotel CRUD stack).
  Migrations still pending — `create_all` until Alembic.
- [x] Place creation flow (API side: auto-fill worker/date). Auto-open add-listings
  page still to do with the frontend.
- [x] Listing entry (API side: create/list/edit, hotel validation). Clickable hotel
  boxes still to do with the frontend.
- [x] Ownership visibility (worker sees own; admin sees all)
- [x] Archiving (manual archive endpoint; archived = admin-only, read-only, terminal)
- [x] Admin queries (`GET /api/admin/reports`: composable filters over archived data,
  totals + per-hotel/per-worker breakdowns, all aggregated in SQL)
- [x] Auto end-of-day archiving (APScheduler daily cron at midnight GMT +
  admin-only `POST /api/places/archive-all` test button; both share one code path)
- [x] Frontend (`app_frontend/`) — **standalone** static HTML + native ES modules +
  `fetch`, no framework, no build, no downloaded deps (dev server is stdlib via
  `.venv`). Implements the "Industry" design handoff: login, role-aware shell, places
  list, place detail + fast listing entry (hotel tiles, inline edit), hotels, users,
  reports. Runs on :5173; API on :8000. Required backend changes: **CORS**
  (`FRONTEND_ORIGIN`) + session cookie `SameSite=none` (`COOKIE_SAMESITE`), and
  `PlaceRead` now carries a `listing_count` (no-N+1 correlated subquery) and serializes
  `date`/`archived_at` as dd/mm/yyyy.
- [x] Plate OCR (`POST /api/ocr/plate`): upload a vehicle photo → YOLOv8 detects the
  plate → RapidOCR reads it → returns `{reg_number}` to pre-fill the form. Two-stage,
  local, offline. `app/ocr/plate_reader.py` is **infrastructure, not a service** (no
  repo — sits beside `security.py`). Model runs in a worker thread (`asyncio.to_thread`)
  so it never blocks the event loop; loaded once, lazily. Requires
  `app/ocr/models/plate_detector.pt` (the MIT YOLOv8 `best.pt`, placed manually) — 503
  until present. Deps: `ultralytics` (pulls Torch CPU), `rapidocr-onnxruntime`, `pillow`,
  `python-multipart`. **Auto model-detect / preset pricing from the screenshot were
  dropped — only the reg number is read** (that's all that was wanted).
- [ ] Email/account delivery (send credentials on account creation) — late dev

## Bugs / Gotchas (hard-won — check here first)
- **`passlib` is dead — do not reintroduce it.** Last release 2020. It reads
  `bcrypt.__about__.__version__`, removed in bcrypt 4.1+, so `passlib[bcrypt]` crashes
  outright with bcrypt 5.x. We call the `bcrypt` package directly in `app/security.py`.
- **FastAPI concatenates dependency lists.** `dependencies=[]` on `include_router` does
  NOT cancel an app-level dependency — it appends. Global auth therefore lives in
  middleware with a `PUBLIC_PATHS` allowlist, never in `FastAPI(dependencies=[...])`.
- **SQLAlchemy `Enum` stores the enum NAME by default** (`"ADMIN"`), not its value
  (`"admin"`), which breaks `Role` comparisons. Always pass
  `values_callable=lambda enum: [item.value for item in enum]`.
- **SQLite has no real timestamp type**, so `DateTime(timezone=True)` is a no-op there:
  values written as aware UTC come back **naive**. Fine today, but date-range admin
  queries must normalise before comparing. Postgres will not have this problem.
- **Pydantic `PlainSerializer` needs `when_used="json"`.** Without it the serializer
  also fires on `model_dump()`, which services use to build ORM objects — so
  `DisplayDate` handed the *string* `"25/12/2026"` to a SQL `Date` column and inserts
  blew up with "SQLite Date type only accepts Python date objects".
- **`HTTP_422_UNPROCESSABLE_ENTITY` is deprecated** in current Starlette; use
  `HTTP_422_UNPROCESSABLE_CONTENT`.
- **`UploadFile` needs `python-multipart`** installed or the route 500s at import/parse
  time — it's not pulled in by FastAPI itself. It's in requirements.txt for the OCR route.
- **`ultralytics` installs PyTorch automatically** (the `.pt` model is a Torch model and
  needs it to run). CPU wheel (`torch ...+cpu`) is correct for a server. OCR (`rapidocr-
  onnxruntime`) runs on onnxruntime, not Torch.
- **`AsyncClient(ASGITransport(...))` does not run lifespan**, so `create_all` never
  fires in tests — create the schema explicitly in test setup.
