# PRD: Acoustic Respiratory Triage for Occupational Lung Disease
### Working name: *Saans Check* ("breath check") — placeholder, not final

**Status:** Pre-build / Phase 0
**Owner:** Mrunmayee
**Last updated:** June 2026

---

## 1. Problem Context

### 1.1 The core problem

Silicosis is a permanent, incurable scarring of the lung caused by inhaling crystalline silica dust. It is endemic among quarry, mine, and stone-processing workers in Rajasthan, Gujarat, and Jharkhand. It is preventable with basic dust suppression and masks, and detectable years before it becomes fatal — but only if workers get screened. Once symptomatic, life expectancy is typically 5–10 years.

The diagnostic gold standard — chest X-ray plus spirometry — requires hospital-grade equipment. Most affected workers are informal laborers in remote sites, hours from the nearest clinic, with no employer obligation to screen them. The result is a population with high disease prevalence and near-zero passive detection.

This is not a hypothetical gap. It is well documented and currently being addressed through periodic government-run screening camps rather than continuous passive monitoring:

- A study of 435 sandstone mine/quarry workers in the Jodhpur belt found 22% symptomatic and 26% with measurable hypoxia, using a referral-camp model with a three-member clinical board.
- Rajasthan's BOCW Welfare Board ran 137 screening camps between 2015–2021, examining 6,809 workers and confirming 3,410 silicosis cases — roughly a 50% hit rate among those who showed up.
- India's Supreme Court has elevated silicosis prevention to a constitutional, Article 21 human-rights obligation, with the National Green Tribunal directing oversight and states running compensation schemes (Rajasthan, Gujarat).

**The gap this project targets is not "no screening exists" — it's "screening is camp-based, periodic, and untargeted."** Camps happen on a schedule, not where disease density is highest, because nobody has a low-cost way to continuously sense where the at-risk population actually is sickest *right now*.

### 1.2 Why a phone microphone is a credible angle — and where the evidence actually stands

Cough-audio AI is real and shipping, but not for this disease yet. Mapping the actual evidence base, not the hoped-for one:

| Claim | Evidence status |
|---|---|
| AI can classify TB from cough audio at meaningful accuracy on a phone | **Validated and shipping.** Salcit Technologies (Hyderabad) runs *Swaasa*, a live India-based TB cough-screening product, built in partnership with Google using the HeAR foundation model (trained on 313M audio clips, ~100M coughs). Backed by the UN's Stop TB Partnership. |
| AI can classify asthma/COPD from cough or respiratory sound | **Validated in research.** Multiple published classifiers (ensemble ML on cough/respiratory signals; HeAR-embedding-based asthma classifiers on pediatric datasets) report 90%+ accuracy in controlled studies. |
| AI can detect silicosis from a biological signal without an X-ray | **Emerging, but not via cough.** A 2025 UNSW study distinguished silicosis patients from healthy controls with over 90% accuracy — using a **breath VOC (volatile organic compound) test analyzed by mass spectrometry**, not cough audio, and not on a phone. It needs a benchtop instrument. This is the closest anyone has come to "X-ray-free silicosis detection," and it's a strong signal that a real biomarker exists — just not yet in a form smartphones can sense. |
| AI can detect silicosis specifically from cough audio | **No published evidence either way.** This has not been studied. It is the central open question of this project, not a solved problem being repurposed. |

**Implication:** the "phone in pocket" insight is sound as an *infrastructure* argument (smartphones are already in workers' hands, cough-AI tooling already exists and is mature for adjacent diseases) but unproven as a *biomarker* argument (nobody knows yet if silicosis leaves a cough signature). The PRD below is built around derisking that second part rather than assuming it.

### 1.3 Why this is being scoped as triage, not diagnosis

This distinction is the legal and ethical spine of the product, not just careful phrasing:

- **Medically:** a phone-based audio classifier cannot and should not replace X-ray/spirometry. Its only legitimate job is to flag who should get the real test sooner.
- **Legally:** India's drug regulator (CDSCO) released 2025 draft guidance classifying standalone software that performs diagnosis, monitoring, or treatment functions as **Software as a Medical Device (SaMD)**, under a four-tier risk system (Class A–D), with Class D — the strictest tier, requiring Central Licensing Authority approval — reserved for AI diagnostic software used in critical situations. A tool that explicitly does *not* diagnose, and only routes people toward camps/clinicians for the real diagnostic, sits in a materially lower risk tier than a diagnostic claim would. This framing is a regulatory strategy, not just a disclaimer — but it does not exempt the product from CDSCO oversight entirely, and that needs to be tracked as the product matures, not assumed away.

---

## 2. What already exists (competitive and infrastructure landscape)

This matters for positioning: **you are not building cough-AI from scratch. You are pointing existing, validated cough-AI infrastructure at a population and disease nobody else is targeting.**

| Player | What they do | Relevance |
|---|---|---|
| **Salcit Technologies / Swaasa** (India) | Live cough-AI product for TB screening, built on Google's HeAR model | Proof that India-market cough-AI screening works, scales, and gets institutional backing (Google, UN Stop TB Partnership). Not focused on silicosis or occupational disease. Potential partner, licensor of underlying tech, or eventual competitor if they expand scope. |
| **Google HeAR** | Foundation model, 313M audio clips / 100M coughs, available via Cloud API to approved researchers | The most powerful available embedding model for this space. Gated access, not a guaranteed-free/open dependency — treat as a Phase 2+ upgrade path, not a Phase 0 dependency. |
| **UNSW silicosis breath-VOC test** | Mass-spec based, 90%+ accuracy, lab/clinic-bound | Strongest evidence that a silicosis-specific biomarker exists at all. Not a competitor (different modality, different deployment context) but the benchmark your acoustic model should be honestly compared against. |
| **Rajasthan/Gujarat government screening camp infrastructure** | BOCW Welfare Board camps, Pneumoconiosis Boards, compensation portals | This is not a competitor — it's the existing distribution and referral channel this product should feed into, not replace. The camps already work; they just don't know where to go next. |

---

## 3. Product Definition

### 3.1 What this is

A mobile-web tool that:
1. Records a short cough sample from a worker via smartphone microphone.
2. Runs it through an audio classifier to flag respiratory-distress acoustic patterns.
3. Returns a simple, local-language, non-alarmist result: "sounds normal, recheck in 3 months" or "possible lung stress — get checked at the next camp or clinic."
4. Logs anonymized, aggregated results by site, feeding a dashboard that helps NGOs and labor welfare boards decide **where to send the next screening camp.**

### 3.2 What this explicitly is not

- Not a diagnostic tool. It never tells a worker they have silicosis.
- Not a replacement for X-ray/spirometry — it is a router toward them.
- Not (in v1) a silicosis-specific detector. It is a general respiratory-distress detector being piloted on a silicosis-risk population, with that gap stated openly to users, partners, and itself.

### 3.3 Core design principle: asymmetric caution

Because silicosis is asymptomatic-until-late and irreversible, a false "you're fine" is more dangerous than a false alarm. The product must be designed so a "normal" result is never the *only* signal a worker receives. Every result — regardless of model output — is paired with **exposure-context information** (years worked, site dust levels if known, mask usage) so "your cough sounds normal" never stands alone as reassurance to ignore continued silica exposure. This is a product requirement, not just a UX nicety — it directly addresses the highest-severity risk in the system.

---

## 4. System Architecture

### 4.1 High-level pipeline

```
[Worker's phone mic]
        |
        v
[1. Recording interface: 5 coughs, ~30 sec, mobile web]
        |
        v
[2. Preprocessing: trim silence, isolate cough events, denoise]
        |
        v
[3. Feature extraction: pretrained audio embedding model (frozen, not trained by us)]
        |
        v
[4. Classifier head: small supervised model we train (the actual ML work)]
        |
        v
[5. Result + exposure-context logic: combine model output with self-reported exposure data]
        |
        v
[6. Local-language result screen: "normal, recheck in 3mo" / "get checked at next camp"]
        |
        v
[7. Anonymized, aggregated upload: site ID + risk tier + exposure data, NOT individual audio]
        |
        v
[8. NGO/welfare-board dashboard: hotspot map, camp prioritization]
```

### 4.2 Component breakdown

**A. Recording interface (mobile web, no app store)**
- Single button: "Cough 5 times" → records → auto-stops.
- Captures alongside: years of dust exposure, mask usage frequency, site/location, optional symptom checklist (already-validated approach — mirrors the Jodhpur-belt referral study's clinical board intake).
- Local language UI (Hindi, Rajasthi/Marwari, Gujarati as primary targets given the worker geography).

**B. Preprocessing**
- Voice activity / cough-event detection to strip silence and background noise (quarry environments are loud — this is a non-trivial real-world engineering problem, not an afterthought).
- Standardize clip length and sample rate to match whatever embedding model is used downstream.

**C. Feature extraction layer — pretrained, frozen, not trained by this project**
This is the "free model" layer. Two tiers, deliberately decoupled so the upgrade path doesn't require re-architecting the product:

- **v1 (build now): YAMNet.** Open, no API key, no usage gating, runs on CPU. Pretrained on AudioSet (general sound categories, includes some cough/respiratory content via self-supervised/weakly-supervised learning on unlabeled audio at scale). Produces a 1024-dim embedding per clip — the input to our classifier.
- **v2+ (upgrade path, gated): Google HeAR.** Purpose-built for exactly this kind of health-acoustic task, trained on 100M+ cough clips specifically, used by Salcit/Swaasa in production. Access is via request to Google Cloud, not an open download — treat as a partnership/access conversation to start once v1 is validated, not a v1 dependency.
- Whisper's audio encoder is a viable fallback if YAMNet underperforms, though it's built for speech, not health acoustics, so YAMNet remains the better-fitted default.

**D. Classifier head — the actual model we train**
- **Learning paradigm: supervised.** This is not ambiguous — we need labeled (audio → outcome) pairs, and no unsupervised or reinforcement approach substitutes for that. Self-supervision is what built the frozen embedding layer above; it is not what produces a usable disease classifier on its own.
- **Architecture: small and simple by design** — logistic regression, SVM, or a shallow MLP on top of the frozen embeddings. This is intentional, not a shortcut: with the limited labeled data realistically available (especially before a silicosis-specific dataset exists), a small classifier head generalizes better and overfits less than a large fine-tuned network. There is no need for a large language model or a fine-tuned 7B+ parameter model anywhere in this pipeline — the task is binary/few-class audio classification, not language generation.
- **Two-stage label strategy (per your direction):**
  - **Stage 1 — public proxy datasets (build now).** Train on Coswara (IISc), the Cambridge COVID-19 Cough dataset, and/or Virufy — all public, labeled, free. These are TB/COVID/healthy-labeled, not silicosis-labeled. The classifier becomes a general "respiratory-distress-pattern vs. healthy" detector, explicitly **not validated for silicosis specifically.** This produces a working, demoable, testable pipeline end-to-end, and is honest scientific scaffolding — but every output, internally and to any user or partner, must be labeled as a proxy model, not a silicosis model, until Stage 2 data exists.
  - **Stage 2 — real silicosis-labeled data (swap-in once available).** Requires partnership with a clinic, hospital, or NGO already running silicosis screening camps (e.g. the Jodhpur-belt referral system, Rajasthan's Pneumoconiosis Boards) to pair X-ray/spirometry-confirmed silicosis cases with cough recordings from the same workers. This is the step that actually answers the open scientific question in §1.2 — does silicosis have a cough signature at all. **No claim of silicosis detection should be made publicly before this stage produces validated results.**

**E. Result + exposure-context logic**
- Combines model output (proxy-respiratory-risk tier) with self-reported exposure data into a single recommendation, so model "normal" results are never presented as standalone reassurance.
- Two-outcome design (per original framing): plain-language, non-alarmist, actionable, in local language.

**F. Aggregation and dashboard**
- Uploads anonymized, site-level data only — risk tier counts, exposure-duration distributions, not raw audio or individually identifying information, by default.
- Dashboard for NGOs/welfare boards: hotspot map by site, trend over repeat visits, camp-prioritization view. This explicitly plugs into the *existing* camp-dispatch workflow already run by Rajasthan's BOCW Welfare Board rather than inventing a new one.

### 4.3 Data and privacy posture

- Raw audio should be processed for feature extraction and then either deleted or retained only with explicit, informed consent, given the sensitivity of health data and the workers' limited bargaining power relative to any employer-adjacent party.
- No data pipeline should allow an employer to access individual worker results. This is a legal exposure point as much as an ethical one — informal-sector workers have essentially no statutory protection if a result reaches an employer.

---

## 5. Regulatory and Legal Considerations

- **CDSCO SaMD framework (2025 draft guidance):** software performing diagnosis/monitoring/treatment functions is classified Class A–D by risk. The "triage, not diagnosis" framing is a genuine strategy to sit in a lower tier, but this needs active tracking as the draft guidance finalizes — it is not a permanent exemption secured by language choice alone.
- **Deployment-channel risk:** liability exposure changes significantly depending on who runs the tool. An independent NGO or welfare board running it as a referral aid carries materially different risk than anything employer-adjacent, even if the employer is just "providing phones." This should be an explicit, early decision in go-to-market, not something resolved implicitly by who happens to fund the pilot.
- **Existing legal infrastructure to plug into, not duplicate:** silicosis is already a compensable injury under the Employees' Compensation Act and Employees' State Insurance Act, and Rajasthan already runs a Pneumoconiosis Board certification and grant-disbursement system. This product's role is improving *targeting* of who gets into that system sooner — not creating a parallel diagnostic or compensation pathway.

---

## 6. Development Phases

### Phase 0 — De-risk the science (before writing product code)
**Goal:** find out whether this is buildable at all before committing to it as a company.
- Literature deep-dive specifically on pneumoconiosis/silicosis acoustic signatures (cough or otherwise) — confirm no existing work has been missed.
- Build the Stage-1 proxy classifier (YAMNet + public TB/COVID datasets) purely as a technical proof that the pipeline works end-to-end, not as a product claim.
- Identify and begin outreach to at least one clinical or NGO partner with access to confirmed silicosis patients (e.g. groups running camps in the Jodhpur sandstone belt, Rajasthan's BOCW-affiliated health centers, OSHAJ-type occupational health NGOs).
- **Exit criterion:** either (a) a partner agrees to a small paired-recording pilot (confirmed cases + cough audio), or (b) enough evidence emerges that the acoustic signal is implausible, in which case pivot the company toward the exposure/symptom-tracking and camp-targeting tool (Phase 1 below) as the standalone product, dropping the acoustic-AI claim entirely rather than shipping an unvalidated one.

### Phase 1 — Ship the wedge that doesn't depend on the model working
**Goal:** build something genuinely useful and revenue/grant-viable even if Phase 0's acoustic question takes years to fully resolve.
- Recording interface + exposure/symptom intake (no AI claim required — structured self-report is valuable on its own, as the Jodhpur referral-camp study demonstrates).
- Aggregation dashboard for NGOs/welfare boards: hotspot identification from self-reported exposure and symptom data alone.
- Pilot with one welfare board, NGO, or occupational-health group already running camps, positioned explicitly as "better targeting data for camps you already run," not as a new diagnostic claim.

### Phase 2 — Stage-1 proxy classifier as an additive feature
**Goal:** add the acoustic layer, clearly labeled as experimental/proxy.
- Integrate the YAMNet-based, public-dataset-trained classifier as an optional, clearly-labeled "experimental respiratory pattern check — not validated for silicosis" feature.
- A/B or shadow-test its output against actual camp outcomes (does a "distress" flag correlate at all with later-confirmed cases?) wherever a partner camp allows it — this is the first real-world signal on whether the proxy approach has any transfer value.

### Phase 3 — Stage-2 silicosis-specific model
**Goal:** answer the actual scientific question.
- Execute the paired clinical dataset collection (confirmed X-ray/spirometry diagnosis + cough recording) with the Phase 0 partner.
- Retrain/replace the classifier head on this data.
- Only at this point does any claim of "silicosis-specific" detection become honest to make — publicly, to users, or to investors.

### Phase 4 — Scale and upgrade path
- Evaluate migrating the embedding layer from YAMNet to Google HeAR (better-fitted, but requires Cloud API access) once the product and validation are mature enough to justify the dependency.
- Evaluate CDSCO SaMD registration pathway formally, with regulatory counsel, once the product is making any health-related claim beyond pure data aggregation.
- Explore integration with existing state systems (Rajasthan's online silicosis registration/certification portal) so flagged workers can be routed directly into the compensation pipeline they're already legally entitled to.

---

## 7. Open Questions

- Who is the realistic first clinical/NGO partner, and what does a paired-data pilot actually require of them (clinic time, consent process, equipment)?
- What's the minimum viable n for a Stage-2 dataset to produce a statistically meaningful first read (likely in the low hundreds, based on the UNSW breath-VOC study's 31-patient cohort as a rough comparator floor)?
- Should Phase 1's dashboard be built as a standalone product/grant pitch in its own right, independent of whether the acoustic angle ever pans out?
- Funding/business model: government welfare-board contract, NGO grant, or direct B2B2C via labor unions — this determines a lot about deployment-channel legal exposure (§5) and should be decided before Phase 1 pilots begin.
