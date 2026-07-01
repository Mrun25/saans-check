# Saans Check — Phase 4: Scale and Upgrade Paths

Three independent upgrade paths, per PRD §6 Phase 4. None of these are blocking for Phases 1-3
to work; all three are specified to a level where the work that *can* be done now (code
structure, research, contact-finding) is done, and the work that genuinely can't be done yet
(gated API access, legal determinations, government relationships) is clearly scoped rather
than guessed at.

## 1. `hear_migration/` — Google HeAR embedding upgrade

YAMNet → HeAR swap-in, ready to activate once Google grants access. Implements the same
`embed()` interface as Phase 2's YAMNet wrapper, so the classifier training/inference code
needs zero changes — only the embedding backend swaps, followed by a retrain (frozen embedding
spaces aren't interchangeable across models even with an identical interface).

## 2. `cdsco_pathway/` — Regulatory self-assessment worksheet

Organizes the actual classification question (Class A-D, per CDSCO's October 2025 draft
guidance) against Saans Check's specific design choices, using the guidance's own two-factor
test (information significance + healthcare situation severity). Explicitly not a legal
opinion — it's a structured starting point for a conversation with real regulatory counsel.

## 3. `state_integration/` — Rajasthan silicosis portal integration spec

Documents what a one-directional, aggregate-only data flow from Saans Check's dashboard into
the state's existing camp-dispatch/Pneumoconiosis Board system would need to look like. No
integration code exists because no API access or government partnership exists yet — this is
a relationship to build after Phase 0/2 produce something concrete to bring to that
conversation, not an engineering task to start now.

## Common thread across all three

Each of these was a genuine research effort during this build (HeAR's actual access pathway,
CDSCO's actual October 2025 draft guidance and its specific classification factors, the
state portal's actual confirmed contact info and camp history) rather than placeholder text.
What's missing in each case is something this project cannot manufacture — gated API approval,
a legal determination, or a government relationship — and the documents say so plainly rather
than implying more progress than has actually been made.
