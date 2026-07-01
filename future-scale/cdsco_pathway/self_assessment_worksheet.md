# CDSCO SaMD Self-Assessment Worksheet

**This is a structured worksheet to organize the regulatory question, not a legal opinion or a
substitute for regulatory counsel.** Classification under India's Medical Devices Rules, 2017
is a legal determination. Nothing in this document should be treated as a final answer about
Saans Check's regulatory status — it exists so that conversation with actual regulatory counsel
starts from an organized picture of the relevant facts, rather than from zero.

## Confirmed regulatory status as of this research (June 2026)

- CDSCO released its **Draft Guidance Document on Medical Device Software** on **October 21,
  2025**, under the Medical Devices Rules (MDR), 2017. As of this research, the 30-day public
  stakeholder consultation period has closed; the **final version has not yet been published**
  — monitor cdsco.gov.in directly for the finalized guidance, since provisions may shift between
  draft and final.
- The draft distinguishes **Software in a Medical Device (SiMD)** — embedded firmware,
  inherits its hardware's risk class — from **Software as a Medical Device (SaMD)** —
  standalone software performing a medical purpose independently. Saans Check, as a standalone
  mobile-web application not embedded in any hardware device, would be assessed as SaMD if it
  is found to perform a medical purpose at all (see the open question below).
- Classification is risk-based, **Class A (lowest) to Class D (highest)**, driven by two
  factors: **(1)** the significance of the information the software provides for a healthcare
  decision, and **(2)** the seriousness of the healthcare situation/condition involved.
- **Licensing pathway differs sharply by class:** Class A requires only online registration
  with CDSCO (no license, fastest path). Class B requires a notified-body QMS audit before a
  State Licensing Authority issues a license (roughly 60–90 days). **Class C and D require
  Central Licensing Authority (CLA) approval** — a materially heavier process (90–120 days for
  Class C, 120–180 days for Class D), potentially including clinical-data submission
  requirements for Class D specifically.
- Where multiple classification rules could apply to one product, the guidance requires
  applying **the strictest rule that results in the highest classification** — relevant if
  Saans Check's "triage, not diagnosis" framing is ever contested, since the worksheet below
  needs to consider the most defensible reading, not the most convenient one.

## The actual classification question for Saans Check

The PRD's core regulatory strategy (§1.3, §5) is that explicitly framing the product as
triage/referral rather than diagnosis keeps it in a lower risk tier. The draft guidance's own
two-factor test gives a structured way to examine whether that framing holds up:

### Factor 1: Significance of information for a healthcare decision

| Question | Saans Check's actual design |
|---|---|
| Does the software's output directly drive a treatment decision? | No — output is a recommendation to seek camp/clinic screening, never a treatment instruction |
| Does the output replace a clinician's independent judgment? | No — the X-ray/spirometry result from a real clinician remains the actual diagnostic event; Saans Check's output exists upstream of that, as a referral trigger |
| Could a "normal" result alone cause a clinician or patient to forgo necessary care? | This is the crux. See `phase1-intake-app/backend/app/result_copy.py` — the asymmetric-caution design (exposure reminder always appended to "normal" results when exposure risk is high) exists specifically to blunt this concern. Whether a regulator agrees this is sufficient mitigation, rather than the product itself making a "fitness to skip screening" determination, is exactly the kind of question regulatory counsel needs to assess directly. |

### Factor 2: Seriousness of the healthcare situation

| Question | Saans Check's actual design |
|---|---|
| Is silicosis a serious/critical condition? | Yes — irreversible, life-shortening once symptomatic (PRD §1.1). This factor alone could push toward a higher class regardless of how the information-significance factor resolves, since the guidance considers both factors and the stricter applicable rule governs. |
| Does this push toward Class C/D regardless of the triage framing? | Plausible, and worth treating as the more conservative planning assumption rather than assuming the lower-risk framing wins outright. The PRD's "lower risk tier" strategy is a credible, real argument — not a guaranteed outcome on the other factor in this same test. |

## Practical recommendation

1. **Do not finalize Saans Check's regulatory positioning based on this worksheet alone.**
   Engage regulatory counsel with specific MDR/SaMD experience once Phase 1 is deployed beyond
   an internal pilot, and certainly before Phase 3's clinical data work begins (paired data
   collection itself may trigger separate clinical-investigation requirements under the MDR,
   independent of the eventual product's own SaMD class — see the CLA Test License / Form MD-23
   process referenced in the regulatory research below).
2. **Track the final guidance**, not just the October 2025 draft — provisions may change
   between draft and final publication.
3. **The Algorithm Change Protocol (ACP)** the draft guidance introduces for AI/ML-based tools
   is directly relevant the moment Stage 1 is swapped for Stage 2 (PRD §6 Phase 3) or YAMNet is
   swapped for HeAR (Phase 4) — these are exactly the kind of "algorithm change" the ACP
   framework is meant to govern, so building basic change-documentation discipline now (model
   version tracking, which `phase2-proxy-classifier/src/train_classifier.py` already does via
   its `model_version` field and saved JSON reports) isn't just good practice, it's likely to
   map directly onto a future compliance requirement.
4. **Revisit deployment-channel risk (PRD §5) alongside this worksheet, not separately** — who
   operates Saans Check (independent NGO vs. anything employer-adjacent) affects liability
   exposure in ways that interact with, but aren't replaced by, the SaMD classification
   question.
