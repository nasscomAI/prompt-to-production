# skills.md — UC-0A Complaint Classifier

**Core failure modes:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

---

## Classification Schema

| Field | Allowed values | Rule |
|---|---|---|
| `category` | Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other | Exact strings only — no variations, sub-categories, or synonyms |
| `priority` | Urgent · Standard · Low | Urgent if severity keywords present; otherwise Standard or Low as appropriate |
| `reason` | One sentence | Must cite specific words from the description |
| `flag` | NEEDS_REVIEW or blank | Set when category is genuinely ambiguous; otherwise blank |

**Severity keywords that must trigger Urgent:**
`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`

---

## Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag. Must follow the Classification Schema above exactly.
    input: A dictionary or JSON object with a "description" field (string) — the text of the citizen complaint. Must reference only the description — no external knowledge, no other rows.
    output: A dictionary or JSON object with fields: category (string), priority (string), reason (string), flag (string). category must be one of the exact allowed values; priority must be Urgent when any severity keyword is found.
    error_handling: If the description is empty or cannot be classified, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the output CSV.
    input: Path to input CSV file containing at least a "description" column. Rows must not have pre-existing "category" or "priority_flag" columns.
    output: Writes a CSV file with columns: category, priority, reason, flag — one row per input row in the same order. Every row must be verifiable against the description alone.
    error_handling: If a row has a missing or empty description, classify it as category "Other", priority "Standard", reason "No description provided", flag "NEEDS_REVIEW". If the input file is missing columns or cannot be read, raise a clear error message.

---

## Common Failure Modes

1. Category names that vary across rows for the same type of complaint
2. Injury/child/school complaints classified as Standard instead of Urgent
3. No reason field in the output
4. Category names that are not in the allowed list
5. Confident classification on genuinely ambiguous complaints
