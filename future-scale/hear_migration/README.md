# Phase 4: HeAR Migration

## Why migrate

Per PRD §1.2/§2: Google's HeAR (Health Acoustic Representations) model is purpose-built for
health-acoustic tasks, trained on 313M audio clips including ~100M coughs specifically — a much
better-fitted embedding model for this use case than YAMNet, which is a general-purpose
AudioSet classifier repurposed for this task. HeAR is the model underlying Salcit Technologies'
production Swaasa TB-screening product in India, confirming it works for this exact category of
problem at production scale.

## Why this isn't done yet

Access is gated. Unlike YAMNet (open download, no API key), HeAR requires a reviewed request to
Google. This is a Phase 4 dependency precisely because the PRD frames it as "upgrade path,
gated... treat as a Phase 2+ upgrade path, not a Phase 0 dependency" (§4.2.C) — the project is
correctly sequenced to not block on this.

## How to request access (confirmed pathway, June 2026)

Google's published intake for HeAR and related Health AI Developer Foundations (HAI-DEF) models
runs through a request-and-review process rather than open self-service download. Search
"Google HAI-DEF HeAR access request" for the current form — intake URLs for gated research
models move periodically, so don't rely on a hardcoded link from this document without
re-verifying it's current.

**When filling out the request, the strongest framing available from this project's actual
status:**
- Specific occupational-health use case (silicosis triage among Rajasthan quarry/mine workers)
  distinct from Swaasa's TB focus — reviewers evaluating requests likely want to see
  differentiated, non-duplicative use cases.
- Reference Salcit/Swaasa as the existing precedent for an India-market cough-AI health product
  built on HeAR, which establishes this is a known-workable pattern Google has already approved
  once for adjacent use.
- Be honest that the biomarker hypothesis (does silicosis have a cough signature) is unvalidated
  — this is a research/derisking request at this stage, not a request to support an
  already-proven product. Overclaiming readiness here would be the same mistake the PRD
  explicitly avoids everywhere else (§1.3, §4.2.D).

## What's implemented here, and what isn't

`hear_embedder.py` implements the same `embed(audio_array, sample_rate) -> np.ndarray`
interface as `../../phase2-proxy-classifier/src/embed_yamnet.py`, so the classifier training
and inference code requires zero changes when this backend goes live — only this file's
`_load_hear_client()` needs the real Google-provided integration code dropped in.

It deliberately raises `NotImplementedError` rather than guessing at HeAR's actual API surface
(REST endpoint? Vertex AI SDK? downloadable checkpoint?) since guessing wrong here would either
fail loudly (acceptable) or — worse — silently call the wrong thing and produce embeddings that
look valid but aren't, which is a much harder bug to catch later. Once Google's access grant
specifies the real integration method, replace the placeholder function body with the actual
client call.

## Migration is a retrain, not a hot-swap

A model trained on YAMNet embeddings cannot be pointed at HeAR embeddings without retraining —
different frozen embedding spaces aren't interchangeable even with an identical calling
interface. The migration path is: extract HeAR embeddings for the same training data (Phase 2's
public datasets, or by then, Phase 3's real clinical data) using
`../../phase2-proxy-classifier/src/extract_embeddings.py` with `embed_yamnet` swapped for
`hear_embedder`, then retrain via `train_classifier.py` exactly as before.
