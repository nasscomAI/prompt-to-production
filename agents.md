# agents.md — UC-0A: Complaint Classifier

## Agent Name
**CivicClassifierAgent**

---

## Role
A civic complaint triage agent that reads raw citizen complaints, determines their
category, assesses severity, and assigns an actionable priority level so that
municipal teams can route and respond efficiently.

---

## Goal
Given a complaint text, output:
- **category** — the municipal department responsible (Roads, Water, Sanitation, Electricity, Public Safety, Other)
- **severity** — impact level (High, Medium, Low)
- **priority** — numeric urgency score (1 = act immediately, 2 = act within days, 3 = schedule routinely)

---

## Backstory
The City of Hyderabad receives thousands of citizen complaints daily via GHMC and
other civic portals. Manual triage is slow, inconsistent, and leaves high-risk
complaints (injuries, children, collapsed infrastructure) buried in queues.
CivicClassifierAgent was designed to automate first-pass triage, ensure no safety
complaint is under-prioritised, and free up human reviewers for edge cases.

---

## RICE Framing

| Dimension | Value |
|-----------|-------|
| **Reach** | All citizen complaints ingested from city CSV feeds |
| **Impact** | Faster routing reduces response time; severity detection protects lives |
| **Confidence** | High — keyword rules are transparent, auditable, and city-tunable |
| **Effort** | Low — rule-based engine, no external API required for baseline |

---

## Decision Rules

1. **Category assignment** — keyword frequency match across 5 department buckets;
   ties broken by first match; unmatched → "Other".
2. **Severity escalation** — starts at Low; presence of urgency keywords → Medium;
   presence of safety/injury/child/hospital/school keywords → High (overrides Medium).
3. **Priority mapping** — deterministic: High→1, Medium→2, Low→3.

---

## Failure Modes Addressed

| Failure | Fix Applied |
|---------|-------------|
| Severity blindness (no safety triggers) | Added `injury / child / school / hospital / fire / accident` as Hard-High triggers |
| Category confusion on mixed complaints | Keyword frequency scoring picks dominant department |
| Silent "Other" for misspelled words | Partial substring match (e.g. "pothl" still misses — known limitation, tunable) |

---

## Limitations
- Does not use an LLM; trade-off is speed and zero API cost vs. nuanced understanding.
- Language: optimised for English; Telugu/Hindi complaints need transliteration layer.
- New complaint types require manual keyword updates.
