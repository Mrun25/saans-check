# Saans Check 🫁
**A privacy-preserving, acoustic respiratory triage tool for occupational lung disease (silicosis) screening.**

> ⚠️ **BUILDING PHASE NOTICE** 
> This project is currently in the active building phase. The machine learning classifier (Phase 2) is a proxy model trained on public TB/COVID datasets and **is not a validated silicosis detector**. It serves as a proof-of-concept for camp prioritization. Do not use this tool for medical diagnosis. See [PRD](docs/PRD.md) for full context.

Saans Check is an open-source, mobile-web platform designed to help NGOs and welfare boards prioritize where to deploy medical camps (X-ray/spirometry trucks) in high-risk occupational environments (e.g., mines, quarries in Rajasthan, India). It combines a worker-facing audio intake flow with privacy-preserving aggregation to build a dashboard for camp prioritization.

## Project Structure

The project is structured into 4 independent phases to ensure the application remains useful even if machine-learning components fail or clinical partnerships are delayed:

1. **`phase1-intake-app/`** (BUILT): The core FastAPI backend and React (Vite) frontend. Includes the mobile-web worker intake flow, privacy-safe aggregation, and the NGO hotspot dashboard.
2. **`phase2-proxy-classifier/`** (BUILT): The YAMNet embedding and generic respiratory-distress classifier pipeline. Acts as an honest proxy until real silicosis data is acquired.
3. **`phase3-clinical-pilot/`** (SCAFFOLDED): Tools for a future clinical partnership, including consent forms and retraining scripts for paired X-ray/audio data.
4. **`phase4-scale/`** (SPEC'D): Upgrade paths including Google HeAR embeddings, regulatory pathway worksheets, and state portal integrations.

## System Architecture

See the [Architecture Documentation](docs/architecture.md) for detailed Mermaid diagrams of the End-to-End Pipeline and the Privacy Boundary Data Flow. 

## Known Issues & Roadmap
- **Model Validation:** The current classifier is trained on generic TB/COVID datasets. It requires paired clinical silicosis data (Phase 3) for true validation.
- **Vercel Deployment Constraints:** Vercel serverless limits (250MB) prevent deploying the full TensorFlow-based Phase 2 model. The deployed demo runs in "exposure-only" graceful degradation mode.
- **Port Conflicts:** The local frontend dev server uses port `5174` (or `5173`) and the backend uses `8001` (or `8000`).

## Deployment

A decoupled demo of Phase 1 (Intake App & Dashboard) is designed to be easily deployed to Vercel. 

### Vercel Setup (Demo Mode)
Because the full machine learning model exceeds Vercel's Serverless Function limits, the Vercel deployment runs in an "exposure-only" mode.
1. `vercel.json` handles routing.
2. `api/index.py` exposes the FastAPI app.
3. `requirements.txt` installs lightweight dependencies only.
```bash
npm i -g vercel
vercel deploy --prod
```

## Phase 4 Documentation
### 1. `hear_migration/` — Google HeAR embedding upgrade
YAMNet → HeAR swap-in, ready to activate once Google grants access.
### 2. `cdsco_pathway/` — Regulatory self-assessment worksheet
Organizes the classification question against CDSCO's draft guidance.
### 3. `state_integration/` — Rajasthan silicosis portal integration spec
Documents aggregate-only data flow specs for future partnerships.
