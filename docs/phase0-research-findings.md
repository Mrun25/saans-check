# Phase 0 Research Findings — De-risking the Science

**Purpose:** the PRD's Phase 0 calls for a "literature deep-dive specifically on
pneumoconiosis/silicosis acoustic signatures" and identification of real partner candidates,
before writing product code. This document is that deep-dive, done June 2026. Every claim below
is sourced; nothing is invented.

---

## 1. Does any published work detect silicosis from cough/respiratory audio specifically?

**Finding: no.** A search across the acoustic-disease-detection literature, the pneumoconiosis
clinical literature, and the major cough-AI research groups (Coswara/IISc, Virufy, COUGHVID/EPFL,
Salcit/Swaasa, Google HeAR's published task list) turned up zero published studies that attempt
silicosis classification from cough or breath *sound*. This matches the PRD's own framing in
§1.2 — the central scientific question is genuinely open, not a solved-but-overlooked problem.

The closest related work is occupational-lung-disease detection via:
- **Breath VOC + mass spectrometry** (UNSW Sydney, Baker et al. 2025, *Journal of Breath
  Research* 19, 026011) — 31 silicosis patients vs. 60 healthy controls, AUC 0.933 using an
  XGBoost classifier on APCI-MS volatile organic compound data, with the iCare Dust Diseases
  Board funding the work. This is a different biological signal (chemical, not acoustic) and a
  different instrument class (benchtop mass spectrometer, not a phone mic) — it confirms a
  silicosis-specific biomarker exists *somewhere* in exhaled breath, but says nothing about
  whether that biomarker has an acoustic correlate.
- **Chest X-ray screening value studies** for engineered-stone-industry silicosis (used as a
  benchmark for what existing screening tools catch and miss).
- **Asbestos-related disease breath VOC studies** (e.g. mesothelioma eNose screening,
  16 healthy / 19 asbestos-exposed / 15 benign-ARD / 14 MPM cohort) — same pattern: VOC/chemical
  signal, not acoustic.

**Implication for this build:** the PRD's "no published evidence either way" framing is correct
and still holds as of this research pass. This is not a gap in this team's literature search —
it is an actual open question in the field. The honest move (and the one this repo takes) is to
build the *infrastructure* now and the *silicosis-specific claim* never, until paired data exists.

## 2. Public proxy datasets — confirmed access status (June 2026)

| Dataset | Status | Size | License/access notes |
|---|---|---|---|
| **Coswara** (IISc Bangalore) | ✅ Open, downloadable now | 2,635 subjects (1,819 SARS-CoV-2 negative, 674 positive, 142 recovered), 9 sound categories per subject, ~65 hours manually quality-annotated | `github.com/iiscleap/Coswara-Data`. IISc Institutional Human Ethics Committee approved; informed consent obtained from all contributors; anonymized. Cite: Bhattacharya et al. 2023, *Scientific Data* (Nature), DOI 10.1038/s41597-023-02266-0. |
| **Virufy** | ✅ Open, downloadable now | 121 single-cough clips from 16 hospital patients (48 PCR-positive, 73 negative), plus larger COUGHVID-sourced standardized subset | `github.com/virufy/virufy-data` and `github.com/virufy/virufy-cdf-coughvid`. Clinical subset collected under physician supervision with informed consent; CC BY 4.0. Small n — useful as a second validation set, not a primary training set. |
| **COUGHVID** (EPFL) | ✅ Open, downloadable now | >25,000 crowdsourced recordings, ~2,800 expert-physician-labeled | Cited widely in the literature as the largest open cough dataset; accessed via the original EPFL release. |

**Action for Phase 2:** train Stage-1 primarily on Coswara (best metadata, ethics provenance,
and scale), use Virufy's clinical subset and COUGHVID's physician-labeled subset as held-out
validation to check the proxy classifier isn't just learning Coswara-specific recording
artifacts. None of these datasets contain silicosis labels — they remain TB/COVID/healthy
proxies, exactly as the PRD specifies, and every output must say so.

## 3. Confirmed real Indian partner candidates for Phase 0 outreach

This is the section that actually moves the project forward. These are not guesses — they are
named organizations with public, current contact information, doing exactly the on-the-ground
work the PRD's Phase 0 needs a partner for.

### Tier 1 — most credible first contact

**Mine Labour Protection Campaign (MLPC) Trust** — Jodhpur, Rajasthan.
- 17+ years working with sandstone mine workers and silicosis victims specifically in the
  Jodhpur belt — the exact population and geography the PRD names.
- Already runs the relevant intake motion: MLPC's Managing Trustee, Rana Sengupta, has
  personally sourced silicosis patients from **K.N. Chest Hospital, Jodhpur**, including a
  900-patient postcard outreach campaign to certified silicosis cases at that hospital.
- Registered nonprofit (Rajasthan Public Charitable Trust Act, 1959) — a legitimate, audit-able
  organizational counterparty, not an informal contact.
- **Contact:** Phone +91-291-2703160, Email `mlpctrust@gmail.com`, 1st Floor, 19/9-B, CHB,
  Jodhpur – 342008, Rajasthan, India. (Source: `minelabour.org`, fetched directly, June 2026.)
- **Why they're the right first call:** they already have the hospital relationship (K.N. Chest
  Hospital) that would let a paired cough-recording + X-ray-confirmation pilot happen without
  starting from zero.

### Tier 2 — strong secondary candidates

**Gramin Vikas Vigyan Samiti (Centre of People's Science for Rural Development)** — Jodhpur.
- Founded by Dr. Prakash Tyagi, a physician; first organization to publicly raise the silicosis
  issue in the Jodhpur belt (1994). Decades of field-camp experience identifying silico-TB cases.
  A physician-led org is a meaningfully different (and useful) partner profile than a labor-rights
  NGO — likely an easier conversation about clinical data collection protocol specifically.

**Dang Vikas Sansthan** — Karauli district.
- Active in Karauli, one of the highest-prevalence districts (studies cited in the PRD and
  confirmed in this research show 38–78% prevalence among quarry workers with >20 years exposure
  in Karauli specifically). A second-district partner would matter for generalizability —
  Jodhpur sandstone and Karauli stone-carving are not identical dust/work profiles.

**Pathar Ghadai Mazdoor Suraksha Sangh (PGMSS)** — Sirohi district.
- Ran field camps and submitted evidence to national occupational health bodies in 2011. Third
  geography, third worker-population profile (carving/grinding rather than open-pit quarrying).

### Tier 3 — government/clinical infrastructure (slower-moving, but the eventual integration point)

**Rajasthan Pneumoconiosis Boards / Silicosis Grant Disbursement Portal**
- Official government helpline: **0141-2928074**, email
  `HELPDESK.SILICOSIS@RAJASTHAN.GOV.IN` (Source: `rajsilicosis.rajasthan.gov.in`, June 2026.)
- 137 screening camps ran 2015–2021 examining 6,809 workers (PRD's own cited figure, independently
  confirmed in this research pass via Oxford Academic's *Annals of Work Exposures and Health* and
  PMC). As of 2025, government plans to add 10 new Pneumoconiosis Boards by 2026 specifically
  citing rural-access gaps — a relevant tailwind for a tool whose whole purpose is improving
  camp targeting.
- **Why not first contact:** government partnerships move slower and require more formal
  procurement/MoU processes. Right sequence: validate with an NGO partner first, bring validated
  results to the state as a "this is what we found with X NGO" pitch, not a cold ask.

### Researchers actively publishing on this exact gap (useful as academic co-investigators, not just citations)

- **Khetan M, Babu BV** — "Silicosis prevalence and related issues in India: a scoping review,"
  *J Occup Med Toxicol*, Jan 2025 — recent enough to reflect the current state of the field.
- **Rupani MP et al.** — multiple 2023–2024 papers specifically on silicosis-TB comorbidity and
  employer-led care models in Indian occupational settings (*Scientific Reports*).
- A 2022 qualitative study (Oxford Academic, *Annals of Work Exposures and Health*) interviewed
  35 stakeholders in Jodhpur district specifically about Pneumoconiosis Policy implementation
  gaps — the author list is a ready-made set of people who already understand this problem space
  and may be open to an advisory or co-investigator role.

## 4. Phase 0 exit criterion — honest current status

The PRD's exit criterion is binary: **(a)** a partner agrees to a paired-recording pilot, or
**(b)** evidence emerges the acoustic signal is implausible (in which case pivot to Phase 1 as
the standalone product).

As of this research pass: **neither has happened, because outreach has not yet been sent.**
This document and `partner-outreach-targets.md` exist so that outreach *can* be sent — they are
the necessary precondition, not the outcome. Nothing in the literature found in §1 supports
condition (b) (implausibility) — there's simply no evidence yet either way, which is the
expected, honest state of an unanswered question, not a red flag.

**Recommended next action, in order:**
1. Send the MLPC outreach email (drafted in `partner-outreach-targets.md`) — they have the
   hospital relationship that shortens the path to a pilot more than any other candidate found.
2. In parallel, build and validate Stage-1 (Phase 2) on Coswara so that any partner conversation
   comes with a working, demoable pipeline rather than a slide deck.
3. If MLPC is unresponsive or declines within 4–6 weeks, move to Gramin Vikas Vigyan Samiti
   (physician-led, may be faster on clinical protocol specifically) or Dang Vikas Sansthan
   (second geography).
