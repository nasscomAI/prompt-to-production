# UC-0A Agents

## Agent: complaint_classifier

### Role
Classify one citizen complaint description into category, priority, reason, and flag using only the row text and the UC-0A schema.

### Success Criteria
- category is exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
- priority is exactly one of: Urgent, Standard, Low.
- reason is one sentence and explicitly cites words from the complaint text.
- flag is NEEDS_REVIEW only when classification is genuinely ambiguous; otherwise blank.

### Hard Enforcement Rules
1. Never invent new or renamed categories.
2. Set priority = Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
3. If evidence is split across multiple plausible categories and no dominant signal exists, set category = Other and flag = NEEDS_REVIEW.
4. Do not use external knowledge; rely only on complaint text.

## RICE-Prioritized Improvements

| Priority | Improvement | Reach | Impact | Confidence | Effort | RICE Score | Why This Matters |
|---|---|---:|---:|---:|---:|---:|---|
| P1 | Strict schema guardrails (exact values + output contract) | 15 | 3 | 0.95 | 1 | 42.75 | Eliminates taxonomy drift and missing fields across all rows. |
| P2 | Deterministic urgency keyword override | 15 | 3 | 0.9 | 1 | 40.50 | Fixes severity blindness for high-risk complaints. |
| P3 | Evidence-based reason sentence requirement | 15 | 2 | 0.9 | 1 | 27.00 | Improves traceability and reviewability of decisions. |
| P4 | Ambiguity fallback (Other + NEEDS_REVIEW) | 15 | 2 | 0.85 | 1 | 25.50 | Prevents false confidence on unclear complaints. |

## Operational Notes
- Input source: ../data/city-test-files/test_[city].csv.
- Output target: uc-0a/results_[city].csv.
- Scope: classification behavior only; no data enrichment or policy inference.
