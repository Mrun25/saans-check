# Saans Check — Phase 2: Stage-1 Proxy Classifier

YAMNet embeddings + a small classifier head, trained on public TB/COVID cough datasets. This is
explicitly **not** a silicosis detector — see `data/README.md` and PRD §4.2.D for why, and
`src/inference.py`'s embedded disclaimer for how that's enforced in the saved model artifact
itself, not just in documentation.

## Pipeline

```bash
pip install -r requirements.txt --break-system-packages

# 1. Download datasets — see data/README.md for exact commands and current access status
git clone https://github.com/iiscleap/Coswara-Data.git data/raw/coswara
git clone https://github.com/virufy/virufy-data.git data/raw/virufy

# 2. Extract embeddings (downloads YAMNet from TF Hub on first run — needs internet access
#    to tfhub.dev specifically)
python src/extract_embeddings.py --dataset coswara --input data/raw/coswara \
    --output data/embeddings/coswara.npz
python src/extract_embeddings.py --dataset virufy --input data/raw/virufy \
    --output data/embeddings/virufy.npz

# 3. Train, holding out Virufy as an honest external check
python src/train_classifier.py --embeddings data/embeddings/coswara.npz \
    --holdout data/embeddings/virufy.npz \
    --output models/stage1_proxy_v1.pkl --model-type logreg

# 4. Evaluate against held-out data with plots
python src/evaluate.py --model models/stage1_proxy_v1.pkl \
    --test-split data/embeddings/virufy.npz --plot
```

## Validation status of this code (important — read before trusting any number)

Every module in `src/` was tested during this build, but **not against the real Coswara/Virufy
datasets**, because downloading and processing tens of thousands of real audio files and
running real YAMNet inference wasn't feasible inside this build session (in particular, this
sandbox's network egress doesn't include `tfhub.dev`, where YAMNet is hosted). Instead:

- `preprocessing.py` was validated against synthetic audio with known injected cough-like
  bursts — the bandpass filter and energy-based event detector correctly isolated a burst
  injected at 1.0–1.3s in a 3-second clip, output 0.99–1.31s.
- `embed_yamnet.py`'s mean-pooling and shape-validation logic was validated against a mocked
  YAMNet model matching YAMNet's documented `(scores, embeddings, spectrogram)` output
  signature — confirmed it returns the expected 1024-dim clip-level embedding, and correctly
  raises on wrong sample rate or wrong array shape.
- `train_classifier.py`, `evaluate.py`, and `inference.py` were run end-to-end against
  synthetic embedding arrays (the right shape and structure real Coswara/Virufy embeddings
  would have) through the full pipeline: train → save → reload → predict → evaluate. This
  confirmed the code runs without errors and that **Phase 1's backend correctly imports and
  calls this Phase 2 model** — a real cross-phase integration test, not just an isolated unit
  test (see `../phase1-intake-app/backend/README.md`).

**What this means practically:** the engineering is real and the integration is proven. The
first time anyone runs this against the actual downloaded Coswara/Virufy data, expect to spend
time on real-world rough edges synthetic data can't surface — Coswara's metadata schema may
have minor field-naming differences from what `datasets.py` assumes (check
`Extracted_data/<any_subject>/metadata.csv` directly against `load_coswara()`'s expectations
before a full run), real AUC will almost certainly be well below the misleadingly perfect 1.0
scores synthetic separable data produces, and YAMNet inference at scale across thousands of
clips will take real wall-clock time worth planning for (a GPU isn't required but will help).

## On model performance expectations

Published cough-AI literature for *adjacent* tasks (TB, COVID, asthma/COPD classification) cited
in `docs/phase0-research-findings.md` reports 80-90%+ accuracy in controlled studies — that's a
reasonable ballpark for what Stage 1 might achieve on Coswara/Virufy's COVID-status labels
specifically. It says nothing about silicosis performance, which is an entirely separate,
currently-unanswered question requiring Phase 3's data.

## Files

| File | Purpose |
|---|---|
| `src/preprocessing.py` | Resample, bandpass filter, cough-event detection |
| `src/embed_yamnet.py` | YAMNet wrapper — the `embed()` interface Phase 4's HeAR module mirrors |
| `src/datasets.py` | Coswara + Virufy loaders with binary label collapse |
| `src/extract_embeddings.py` | CLI: dataset → embeddings .npz |
| `src/train_classifier.py` | CLI: embeddings → trained classifier pipeline (.pkl) |
| `src/evaluate.py` | CLI: evaluate a trained model against any embedding set |
| `src/inference.py` | The `ProxyClassifierPipeline` class Phase 1's backend imports |
