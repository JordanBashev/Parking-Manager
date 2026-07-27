# app_frontend

Standalone frontend for Managining — static HTML + native ES modules + `fetch`. 

## Run it

Both use the project `.venv`

```
.venv\Scripts\python app_frontend/serve.py
```

Then open <http://localhost:5173>. Sign in with an account made by `seed_admin.py`.

## Structure

```
index.html          shell: #nav, #main, toast + dialog roots; loads js/main.js
styles.css          the "Industry" design system, used as-is (do not edit)
app.css             a few app-only helpers (.num, .row-link, .tile:hover)
serve.py            stdlib dev server with SPA fallback (clean-path refreshes work)
js/
  config.js         API base URL (one place to repoint the backend)
  api.js            fetch wrapper: credentials, JSON, ApiError (401/403/404/409/422)
  dates.js          dd/mm/yyyy <-> yyyy-mm-dd at the <input type=date> boundary
  state.js          session + isAdmin()
  router.js         clean-path History router (/place/:id etc.)
  nav.js            role-aware top bar
  layout.js         content column, data table, empty state
  ui.js             el() DOM builder, blueprint frame, corner marks, toast, dialog
  main.js           boot: load session, register routes, start router
  screens/          one module per screen: login, places, place, hotels, users, reports
```

Each screen exports a `render()` and owns its own event wiring. `api.js`, `dates.js`
and `ui.js` are the shared spine.