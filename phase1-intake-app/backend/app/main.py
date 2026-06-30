import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import dashboard, sites, submissions

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Saans Check API",
    description=(
        "Acoustic respiratory triage backend. NOTE: this API never makes a silicosis "
        "diagnosis claim. See docs/PRD.md §3.2 and app/result_copy.py."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the deployed frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions.router)
app.include_router(sites.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
