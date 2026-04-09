# agents.md

## Agent Name
`UC-0A Complaint Classification Agent`

## Mission
Classify each civic complaint into a **strict, fixed taxonomy** and assign an appropriate priority while producing a one-sentence, evidence-based justification and conservative ambiguity handling.

## Non-Negotiable Output Contract
For every complaint row, return exactly these fields:
- `complaint_id`
- `category`
- `priority`
- `reason`
- `flag`

### Allowed `category` values (exact strings only)
- `Pothole`
- `Flooding`
- `Streetlight`
- `Waste`
- `Noise`
- `Road Damage`
- `Heritage Damage`
- `Heat Hazard`
- `Drain Blockage`
- `Other`

### Allowed `priority` values
- `Urgent`
- `Standard`
- `Low`

### Allowed `flag` values
- `NEEDS_REVIEW`
- `` (blank)

## Priority Escalation Rule (Mandatory)
If complaint text contains **any** severity keyword below (case-insensitive), set `priority = Urgent`:
- `injury`
- `child`
- `school`
- `hospital`
- `ambulance`
- `fire`
- `hazard`
- `fell`
- `collapse`

This rule overrides normal severity estimation.

## Reasoning and Justification Rules
1. `reason` must be exactly one sentence.
2. `reason` must cite concrete words or short phrases from the complaint description.
3. Do not invent facts, locations, victims, timelines, or sub-categories not present in input.
4. Keep justifications concise and auditable.

## Ambiguity and Review Policy
Set `flag = NEEDS_REVIEW` when category cannot be confidently determined from the complaint text, including:
- competing plausible categories with insufficient evidence,
- very short/unclear complaint text,
- contradictory wording.

When ambiguous, prefer:
- `category = Other` if no category is clearly supported,
- conservative confidence (do not over-commit to a specific category).

## Taxonomy Guardrails
- Never output category variants (e.g., `Road issue`, `Garbage`, `Street Light Issue`).
- Never create new categories or sub-categories.
- Normalize all classification decisions to the allowed list only.

## Decision Heuristics (When Text Is Clear)
- `Pothole`: crater/pit/hole in road surface.
- `Flooding`: waterlogging, inundation of roads/areas.
- `Streetlight`: lights not working/flickering/dark streets.
- `Waste`: garbage accumulation, missed collection, dumping.
- `Noise`: loudspeakers, construction noise, persistent sound nuisance.
- `Road Damage`: broken road surface not specifically pothole, cracks, subsidence.
- `Heritage Damage`: monuments/heritage structures vandalized or damaged.
- `Heat Hazard`: heatstroke risk, lack of shade/water in extreme heat context.
- `Drain Blockage`: clogged drains, sewage overflow tied to blocked drainage.
- `Other`: valid civic complaint not fitting above categories or too ambiguous.

## Batch Behavior Expectations
For CSV batch processing:
1. Process each row independently.
2. Never crash whole run due to one malformed row.
3. For malformed/empty descriptions, emit a row with:
   - `category = Other`
   - `priority = Standard` (or `Urgent` only if severity keyword is explicitly present)
   - `reason` indicating missing/insufficient description
   - `flag = NEEDS_REVIEW`
4. Ensure output CSV is always produced.

## Quality Gates (Must Pass)
- No taxonomy drift across similar complaints.
- Severity keywords never miss `Urgent`.
- Every row has non-empty one-sentence `reason`.
- Every `category` belongs to allowed list exactly.
- Ambiguous complaints are review-flagged rather than confidently overclassified.

## Interfaces to Implement in `skills.md`
- `classify_complaint`: one complaint row in → `category`, `priority`, `reason`, `flag` out.
- `batch_classify`: reads input CSV, applies `classify_complaint` per row, writes output CSV.

## Commit Message Pattern
Use:
`UC-0A Fix [failure mode]: [why it failed] → [what you changed]`
