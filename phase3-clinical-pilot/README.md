# Saans Check — Phase 3: Clinical Pilot Scaffolding

**Status: code complete, blocked on a real partnership — not blocked on engineering.**

This phase answers the PRD's actual open scientific question (§1.2): does silicosis have a
cough-acoustic signature at all? Nobody knows, because nobody has ever paired confirmed
silicosis diagnoses with cough recordings. This folder is everything needed to find out the
moment a real clinical/NGO partner agrees to a pilot — see
`../docs/partner-outreach-targets.md` for who that might be and a ready-to-send email.

## What's here

| File | Purpose |
|---|---|
| `consent_forms/consent_form_draft.md` | Hindi + English informed consent draft (needs IRB/ethics review before real use) |
| `data_schema/schema.py` | Data model for paired audio + clinical diagnosis records, using the real ILO pneumoconiosis staging system |
| `data_schema/sample_size_notes.md` | How many paired recordings are actually needed for a meaningful first read |
| `scripts/retrain_stage2.py` | Retraining script — reuses Phase 2's classifier training code, pointed at real data |

## What's deliberately NOT here

There is no synthetic or placeholder "silicosis dataset" anywhere in this folder. Faking one,
even labeled as fake, risks someone later mistaking it for real data, or worse, the project
quietly treating Phase 2's TB/COVID proxy labels as silicosis labels under deadline pressure —
exactly the failure mode PRD §1.3 and §4.2.D exist to prevent. `retrain_stage2.py` was tested
during this build against a manifest of *structurally valid but fake* audio/label pairs purely
to confirm the code runs correctly end-to-end (loader → embedding extraction → Phase 2's
training script → disclaimer rewrite) — that test data was deleted after confirming the
pipeline works, not shipped in this repo.

## How this activates

1. Outreach (see `../docs/partner-outreach-targets.md`) produces a partner willing to do a
   paired-recording pilot.
2. The partner's ethics committee or an independent IRB reviews and approves a finalized
   version of `consent_forms/consent_form_draft.md`.
3. Recordings + diagnoses are collected per `data_schema/schema.py`'s structure, written to a
   `manifest.csv` (columns: `participant_id`, `audio_filepath`, `silicosis_label`, plus whatever
   exposure/diagnosis fields the partner's intake process captures).
4. Run:
   ```bash
   python scripts/retrain_stage2.py --paired-data-dir /path/to/collected/data \
       --output ../phase2-proxy-classifier/models/stage2_silicosis_v1.pkl
   ```
5. Evaluate using `../phase2-proxy-classifier/src/evaluate.py` against a held-out split of the
   real data — same evaluation tooling as Stage 1, applied to Stage 2's real labels.
6. Only at this point does any claim of silicosis-specific detection become honest to make
   (PRD §6, Phase 3 goal) — and only if the sample size and evaluation results actually support
   it, per `data_schema/sample_size_notes.md`.
