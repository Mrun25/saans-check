# System Architecture — All Phases

## End-to-end pipeline (per PRD §4.1)

```mermaid
flowchart TD
    WorkerMic["Worker's phone mic"] --> Phase1Intake["1. Recording interface (Phase 1, BUILT)\n<i>mobile web, no app store, Hindi/Marwari/Gujarati</i>"]
    Phase1Intake --> Phase2Preprocess["2. Preprocessing (Phase 2, BUILT)\n<i>trim silence, isolate cough events, denoise, resample</i>"]
    Phase2Preprocess --> Phase2Embed["3. Feature extraction\n<i>v1: YAMNet (Phase 2, BUILT)</i>\n<i>v2: Google HeAR (Phase 4, SPEC'D)</i>"]
    Phase2Embed --> Phase2Classifier["4. Classifier head (Phase 2, BUILT)\n<i>Stage 1: trained on proxy datasets</i>\n<i>Stage 2: retrained on clinical data (Phase 3)</i>"]
    Phase2Classifier --> Phase1Result["5. Result + exposure-context logic (Phase 1, BUILT)\n<i>combines model tier with self-reported exposure</i>"]
    Phase1Result --> Phase1Screen["6. Local-language result screen (Phase 1, BUILT)"]
    Phase1Screen --> Phase1Upload["7. Anonymized aggregate upload (Phase 1, BUILT)\n<i>NEVER raw audio, NEVER identifying data</i>"]
    Phase1Upload --> Phase1Dash["8. NGO/welfare-board dashboard (Phase 1, BUILT)\n<i>hotspot map, camp-prioritization view</i>"]

    classDef builtin fill:#f3e3cc,stroke:#5e3320,stroke-width:2px;
    class WorkerMic,Phase1Intake,Phase2Preprocess,Phase2Embed,Phase2Classifier,Phase1Result,Phase1Screen,Phase1Upload,Phase1Dash builtin;
```

## Why Phase 1 and Phase 2 are decoupled

Phase 1 (intake + dashboard) makes zero AI claims and is valuable on its own — the PRD is
explicit about this (§6, Phase 1 goal: "ship the wedge that doesn't depend on the model
working"). The backend API is built so the classifier result is an *optional field* on a
submission, not a required one. If Phase 2's model never clears validation, Phase 1 ships and
operates standalone with structured self-report data alone, exactly as the PRD's exit
criterion (b) describes.

## Why the classifier head is small (per PRD §4.2.D)

The embedding layer (YAMNet now, HeAR later) is a frozen, pretrained, self-supervised model —
it is not retrained by this project. The only thing this project trains is a small classifier
head (logistic regression / SVM / shallow MLP) on top of those frozen embeddings. This is
deliberate: with low hundreds of labeled examples (the realistic Stage 2 ceiling — see
`phase3-clinical-pilot/data_schema/sample_size_notes.md`), a large fine-tuned network overfits
and a small linear/shallow head generalizes better. There is no LLM anywhere in the disease
classification path — this is binary/few-class audio classification on fixed-size embeddings,
not language generation. (The optional LLM-powered result-phrasing layer, used only to translate
a *fixed, pre-approved* set of result strings into natural local-language phrasing, is described
separately in `phase1-intake-app/backend/app/result_copy.py` and never sees raw model scores.)

## Data flow and privacy boundary

```mermaid
sequenceDiagram
    participant Worker as Worker's phone
    participant Backend as Backend (Phase 1)
    participant Dashboard as NGO Dashboard

    Worker->>Backend: Record 5 coughs + exposure form
    Note over Backend: Preprocess + embed
    Note over Backend: Run classifier head
    Note over Backend: Generate result text
    Note over Backend: DELETE raw audio after embedding
    Backend-->>Worker: [Individual result]<br/>Shown ONLY to the worker.<br/>No employer-facing path exists.
    Backend->>Dashboard: Anonymized Site Aggregates
    Note over Dashboard: Hotspot map<br/>Risk tiers by site<br/>(No audio, no worker IDs)
```

This boundary — raw audio deleted post-embedding by default, individual results never leaving
the worker's device, only site-level aggregates reaching the dashboard — is implemented in
`phase1-intake-app/backend/app/privacy.py` and is not optional/configurable by a deploying
organization without an explicit code change, by design (see PRD §4.3 and §5).

## Phase 3/4 integration points (specified, not yet activated)

- **Phase 3** plugs into step 4 above: the *same* classifier-head training code
  (`phase2-proxy-classifier/src/train_classifier.py`) is reused, pointed at a different,
  paired-clinical dataset once one exists. See `phase3-clinical-pilot/scripts/retrain_stage2.py`
  — it imports directly from the Phase 2 module rather than forking it, so Stage 1 → Stage 2 is
  a data swap, not a rewrite.
- **Phase 4 (HeAR)** plugs into step 3: `phase4-scale/hear_migration/hear_embedder.py`
  implements the same interface as `phase2-proxy-classifier/src/embed_yamnet.py`
  (`embed(audio_array, sample_rate) -> np.ndarray`), so the classifier head doesn't need to
  change at all when the embedding backend changes.
- **Phase 4 (CDSCO)** is a standalone worksheet — see `phase4-scale/cdsco_pathway/` — since
  regulatory classification is a legal determination this repo cannot make, only document.
- **Phase 4 (state portal)** is an integration spec — see `phase4-scale/state_integration/` —
  since it requires API credentials this project does not have and a government partnership
  this project has not yet secured (per the Phase 0 outreach status).
