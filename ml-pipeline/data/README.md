# Datasets — how to get them

None of these datasets are redistributed in this repo. They're public, ethics-board-approved
research datasets with their own licenses and citation requirements — download them yourself
following the instructions below. All three were confirmed live and accessible as of June 2026.

**None of these contain silicosis labels.** They are TB/COVID/healthy-labeled proxy datasets,
exactly as PRD §4.2.D specifies. The classifier trained on them is a general
"respiratory-distress-pattern vs. healthy" detector, not a silicosis detector, and every part of
this codebase that touches their output says so.

## 1. Coswara (primary training set)

- **What it is:** 2,635 subjects, 9 sound categories each (including cough, breathing, vowel
  sounds), COVID-19 status labels (1,819 negative / 674 positive / 142 recovered), ~65 hours
  manually quality-annotated.
- **Get it:**
  ```bash
  git clone https://github.com/iiscleap/Coswara-Data.git data/raw/coswara
  cd data/raw/coswara
  python extract_data.py   # the repo's own extraction script — unpacks the per-subject zips
  ```
- **License/ethics:** IISc Bangalore Institutional Human Ethics Committee approved; informed
  consent obtained from all contributors; data anonymized.
- **Cite:** Bhattacharya, D. et al. (2023). "Coswara: A respiratory sounds and symptoms dataset
  for remote screening of SARS-CoV-2 infection." *Scientific Data* 10, 397.
  DOI: 10.1038/s41597-023-02266-0

## 2. Virufy (held-out validation set)

- **What it is:** 121 single-cough clips from 16 hospital patients (48 PCR-positive coughs, 73
  negative), collected under physician supervision. Use this as a held-out check, NOT primary
  training data — n is too small to train on alone, but valuable for checking the
  Coswara-trained classifier isn't just learning Coswara-specific recording artifacts.
- **Get it:**
  ```bash
  git clone https://github.com/virufy/virufy-data.git data/raw/virufy
  ```
  A separate, larger COUGHVID-sourced standardized subset is also available at
  `github.com/virufy/virufy-cdf-coughvid` if more validation volume is needed.
- **License:** CC BY 4.0.

## 3. COUGHVID (second held-out validation set)

- **What it is:** >25,000 crowdsourced cough recordings, with a subset of ~2,800 expert
  physician-labeled (COVID-status + some respiratory-condition labels).
- **Get it:** the original EPFL release — search "COUGHVID dataset EPFL Zenodo" for the current
  Zenodo record, since hosting location can move; verify the DOI matches the dataset described
  in the original publication (Orlandic et al. 2021, *Scientific Data*) before using.

## Expected directory structure after download

```
data/raw/coswara/Extracted_data/<subject_id>/cough-heavy.wav, ...
data/raw/virufy/...
data/raw/coughvid/...
```

`src/extract_embeddings.py` expects this layout by default — pass `--input` to point at
wherever you actually put things if it differs.

## A note on what's NOT here, and why

There is no `data/raw/silicosis/` folder, and there won't be one until Phase 3 produces real,
consented, paired clinical data through an actual partnership (see
`../phase3-clinical-pilot/README.md` and `../docs/partner-outreach-targets.md`). Faking this
folder with synthetic data, or quietly treating TB-positive labels as a silicosis proxy in
training, would produce a model that looks like it does something it doesn't — which is exactly
the failure mode PRD §1.3 and §4.2.D are written to prevent. Don't do it, even for a demo.
