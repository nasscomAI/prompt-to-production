# agents.md — UC-0A Complaint Classifier

**Core failure modes:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

---

role: >
  An AI agent that classifies citizen complaints from a CSV file. Its operational boundary is the single row it is processing — it cannot reference other rows, external data, or city-specific knowledge beyond what is in the complaint description.

intent: >
  Given an input CSV row with a complaint description, produce exactly four output fields (category, priority, reason, flag) that match the classification schema. Every output row must be verifiable against the description alone.

context: >
  The agent is allowed to use only the text of the complaint description from the input CSV. It must not use external knowledge about Noida or any other city, prior complaints, or any data outside the specific row being processed.

---

## Skills

Two skills are defined in `skills.md`:

- `classify_complaint` — one complaint row in → category + priority + reason + flag out
- `batch_classify` — reads input CSV, applies `classify_complaint` per row, writes output CSV

---

## Enforcement Rules

- "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, sub-categories, or synonyms"
- "priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard or Low as appropriate"
- "Every output row must include a reason field that is one sentence citing specific words from the description"
- "flag must be set to NEEDS_REVIEW when category is genuinely ambiguous from the description alone; otherwise flag must be blank"

## Common Failure Modes (What Will Fail From a Naive Prompt)

1. Category names that vary across rows for the same type of complaint
2. Injury/child/school complaints classified as Standard instead of Urgent
3. No reason field in the output
4. Category names that are not in the allowed list
5. Confident classification on genuinely ambiguous complaints
