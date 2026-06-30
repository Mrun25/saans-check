# Phase 4: Rajasthan State Silicosis Portal Integration — Spec

**Status: specification only. No integration code exists, because no API credentials or formal
government partnership exist yet.** This document describes what the integration would need to
look like, so that if/when a government partnership materializes (PRD §6 Phase 4: "explore
integration with existing state systems... so flagged workers can be routed directly into the
compensation pipeline they're already legally entitled to"), the engineering work is scoped
rather than starting from zero.

## What exists today (confirmed, June 2026)

- Rajasthan runs an official silicosis portal/helpdesk: helpline **0141-2928074**, email
  `HELPDESK.SILICOSIS@RAJASTHAN.GOV.IN` (see `../../docs/phase0-research-findings.md` and
  `../../docs/partner-outreach-targets.md` for sourcing).
- The state's Pneumoconiosis Board system already certifies silicosis cases and disburses
  compensation grants under the Employees' Compensation Act / Employees' State Insurance Act
  framework (PRD §5).
- 137 screening camps ran 2015–2021, examining 6,809 workers and confirming 3,410 cases — this
  existing camp-dispatch and certification workflow is exactly what Phase 1's dashboard (PRD
  §4.2.F) is meant to feed better targeting data into, not replace.

## What's NOT confirmed

- Whether the state portal exposes any public or partner-accessible API at all. No API
  documentation was found in this research pass — government portals of this kind often don't
  expose one, or only do so through a formal MoU/data-sharing-agreement process rather than
  open developer access.
- What authentication/authorization model any such integration would require.
- Whether the state would even want an external NGO tool feeding data into camp-dispatch
  decisions without a formal evaluation/certification process of its own — this is a
  relationship and trust question at least as much as a technical one.

## What this integration would need to do, if/when it becomes possible

1. **One-directional data flow, dashboard to state, not the reverse.** Saans Check's
   site-level aggregate hotspot data (the same data shown in
   `phase1-intake-app/frontend/src/components/Dashboard.jsx`) would be submitted as a
   camp-prioritization input signal, never the other direction. There's no current PRD basis
   for Saans Check needing to read individual worker records from the state's compensation
   system, and building that would introduce exactly the kind of individual-identifying data
   flow the privacy architecture (PRD §4.3, `phase1-intake-app/backend/app/privacy.py`) is
   designed to prevent.
2. **Aggregate-only payload**, structurally identical to the `AggregateSiteStatsOut` schema
   already defined in `phase1-intake-app/backend/app/schemas.py` — site code, district,
   submission counts, risk tier distribution, exposure-pattern summary. No individual worker
   data in the payload, ever.
3. **Explicit non-diagnostic framing in the data contract itself** — any integration spec
   negotiated with the state should encode, in the API contract or MoU language, that this is
   a targeting-prioritization signal feeding into the state's own existing camp-dispatch
   decision process, not a diagnostic claim the state is being asked to act on automatically.
   This mirrors the regulatory strategy in PRD §1.3/§5 and `cdsco_pathway/`.
4. **A formal data-sharing agreement**, not just an API key, given that this is health-adjacent
   occupational data about identifiable communities (even though no individual is identifiable
   in the payload, site-level data about which villages/quarries have high rates can itself be
   sensitive to the workers and communities involved).

## Recommended next step

This is not an engineering task to start now. It's a relationship to build after Phase 0
outreach (NGO/clinical partner) and Phase 2 validation produce something concrete enough to
bring to a government conversation — per the sequencing note in
`../../docs/partner-outreach-targets.md`: "government partnership conversations move faster
with a validated pilot result from an NGO partner in hand... than as a cold ask." The right
state contact for that eventual conversation is the helpdesk listed above, but only once there's
a real result to bring them, not before.
