# Saans Check — Frontend (Phase 1)

Mobile-web app (no app store) for the worker-facing recording + exposure-intake flow, plus a
simple `/dashboard` route for NGO/welfare-board staff.

## Setup

```bash
npm install
npm run dev      # starts on http://localhost:5173, proxies /api to http://127.0.0.1:8000
```

Make sure the backend (`../backend`) is running on port 8000 first — see its README.

## Routes

- `/` — worker flow: language → exposure intake → cough recording → result
- `/dashboard` — NGO/welfare-board hotspot view (reads only from the aggregate API)
- `/?site=JDH-KaliBeri-01` — pass a site code via URL param (e.g. from a QR code printed at
  the camp/site). Defaults to `JDH-KaliBeri-01` if omitted — change this default or wire up
  real per-site QR codes before any real deployment.

## Design notes

The visual language intentionally avoids the generic medical blue/white look. The audience is
quarry/mine workers using basic phones outdoors, often in bright sun and dust, during a work
break — so: warm sandstone/terracotta palette (matches the actual material world), large
single-tap targets throughout (no typing required anywhere in the worker flow), high contrast
for outdoor visibility, and a deliberately oversized record button as the one moment in the
flow that deserves visual weight. See `src/styles.css` for the token definitions.

## Translation status

Hindi and English strings in `src/locales/strings.js` are complete drafts. Marwari (`mwr`) and
Gujarati (`gu`) are NOT yet translated — the language picker includes them per the PRD's target
geography, but `t()` currently falls back to Hindi/English for those codes. **Do not deploy to
a Marwari- or Gujarati-primary site without getting those translated and reviewed by a native
speaker first** — silently falling back to Hindi for a Gujarati-speaking worker is a usability
problem, not just an incomplete-feature problem, given this product's population.

## Building for production

```bash
npm run build   # outputs to dist/
```

Serve `dist/` from any static host; point the backend URL via the Vite proxy config (dev) or
your reverse proxy config (production) at `/api`.
