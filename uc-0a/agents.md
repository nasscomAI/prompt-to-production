# agents.md — UC-0A Complaint Classifier

role: >
  UC-0A — Complaint Classifier

intent: >
  Classify citizen complaints and avoid core failure modes: Taxonomy drift, Severity blindness, Missing justification, Hallucinated sub-categories, False confidence on ambiguity.

context: >
  15 rows per city. `category` and `priority_flag` columns are stripped — you must classify them.

enforcement:
  - "Category: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other (Exact strings only — no variations)"
  - "Priority: Urgent · Standard · Low (Urgent if severity keywords present: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)"
  - "Reason: One sentence (Must cite specific words from description)"
  - "Flag: NEEDS_REVIEW or blank (Set when category is genuinely ambiguous)"
