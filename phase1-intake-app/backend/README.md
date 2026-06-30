# Saans Check — Backend (Phase 1)

FastAPI backend: exposure intake, optional cough-audio classification, privacy-safe aggregation,
and the dashboard API.

## Setup

```bash
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
# API docs at http://127.0.0.1:8000/docs
```

Defaults to SQLite (`saans_check.db` in this folder). For production, set:

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/saans_check"
```

## Running without the Phase 2 classifier installed

This backend works completely fine with zero acoustic model deployed — this is the point of
Phase 1 (PRD §6: "ship the wedge that doesn't depend on the model working"). Submissions without
the optional `/audio` call, or where no `STAGE1_MODEL_PATH` env var is set, simply return
`risk_tier: "no_audio_submitted"` or `"model_unavailable"` and the rest of the app (exposure
intake, aggregation, dashboard) works identically either way.

## Enabling the Phase 2 classifier

```bash
export STAGE1_MODEL_PATH=/path/to/phase2-proxy-classifier/models/stage1_proxy_v1.pkl
```

See `../../phase2-proxy-classifier/README.md` to train this model first.

## Running the aggregation job

```bash
python -m app.aggregation
```

In production, schedule this via cron or a task queue (Celery/RQ) to run nightly. It's the only
code path allowed to read individual `Submission` rows and is the privacy boundary described in
`app/privacy.py` and `docs/architecture.md`.

## API overview

| Endpoint | Purpose |
|---|---|
| `POST /api/sites` | Register a new quarry/mine site |
| `GET /api/sites` | List sites |
| `POST /api/submissions` | Exposure intake (no audio required) |
| `POST /api/submissions/{id}/audio` | Attach + classify a cough recording |
| `GET /api/dashboard/hotspots` | Aggregate-only, privacy-safe camp-prioritization view |
| `GET /health` | Liveness check |

Full interactive docs (request/response schemas) at `/docs` once running.

## Tests

No automated test suite is included in this scaffold — the functional flow was verified
manually during this build (site creation → exposure intake → audio attach with model
unavailable → aggregation rollup → dashboard read). Adding `pytest` coverage for
`app/result_copy.py` (the exposure-reminder logic) and `app/privacy.py` (the export-boundary
checks) would be the highest-value first tests to write, since those two modules encode the
PRD's core safety requirements (§3.3, §4.3, §5).
