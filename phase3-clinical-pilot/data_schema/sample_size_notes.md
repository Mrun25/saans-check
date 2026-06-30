# Sample Size Notes — Phase 3 Paired Clinical Pilot

This addresses the PRD's open question (§7): "What's the minimum viable n for a Stage-2 dataset
to produce a statistically meaningful first read?"

## Comparator: the UNSW breath-VOC study

The closest available comparator — a different modality (breath VOC vs. cough audio) attempting
a structurally similar task (distinguish confirmed silicosis from healthy controls using a
phone-incompatible biological signal) — is Baker et al. 2025 (*Journal of Breath Research*),
which used **31 silicosis patients vs. 60 healthy controls** (91 total) and achieved an AUC of
0.933 with an XGBoost classifier on mass-spec VOC data. This is a reasonable floor-level
comparator for "how many confirmed cases does it take to get a first meaningful read," though
not a guarantee acoustic signal behaves the same way.

## Recommended phased target

- **Pilot phase (proof of feasibility, not statistical power):** 30–50 paired recordings total,
  split roughly evenly between confirmed silicosis cases (any ILO category 1+) and confirmed
  silica-exposed-but-healthy controls (ILO category 0, ideally matched on years of exposure).
  This is enough to tell, qualitatively, whether the embeddings even separate at all when
  visualized (e.g. via a simple logistic regression AUC and a t-SNE plot) — not enough for a
  publishable result, but enough to decide whether to invest in a larger collection effort.

- **First statistically meaningful read:** 100–150 paired recordings (matching the same rough
  order of magnitude as the UNSW study, scaled up modestly since acoustic signals plausibly need
  more samples than a direct chemical assay to overcome recording-condition noise). At this
  scale, a simple classifier head (per Phase 2's "small and simple by design" approach) can
  produce a defensible AUC estimate with a reportable confidence interval.

- **Validation-grade dataset:** 300+ paired recordings, ideally across at least two of the
  partner geographies identified in `../../docs/partner-outreach-targets.md` (e.g. Jodhpur
  sandstone + Karauli stone-carving), to check the signal generalizes across different dust
  compositions and work types rather than being an artifact of one site's recording conditions.

## What determines real-world feasibility, not just statistical preference

The actual constraint is not statistics — it's how many confirmed silicosis cases a partner
organization sees in a tractable timeframe. MLPC's documented work with K.N. Chest Hospital
(see `../../docs/phase0-research-findings.md`) suggests case volume exists; the real open
question for a first conversation with a partner is how many of those cases could realistically
be approached for consent and paired recording within, say, a 6-month pilot window — which is
exactly the kind of question the outreach email in
`../../docs/partner-outreach-targets.md` is designed to surface.

## What NOT to do under sample-size pressure

Do not pad a small real silicosis cohort with TB/COVID-positive cases from the Phase 2 proxy
datasets and call the combined set "silicosis training data." Those conditions are not the same
disease and conflating them would produce a model that looks validated but isn't — this is the
exact failure mode the PRD's two-stage label strategy (§4.2.D) exists to prevent. If the n is
too small for a meaningful first read, the honest move is to say so and keep collecting, not to
quietly dilute the dataset's labels.
