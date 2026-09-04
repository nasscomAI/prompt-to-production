# agents.md — UC-0A Complaint Classifier
# Vibe Coding Workshop | RICE → CRAFT | Civic Tech Edition
# Author: Sneha (participant/Sneha-Amritsar) | City: Amritsar/Pune validation on 4 cities

role: >
  Complaint Classifier Agent — Classifies citizen complaints from municipal CSVs into a fixed taxonomy and assigns priority. Operates strictly within the `description` field of the input row; no external data, inference, or personal interpretation.

intent: >
  Produce a verifiable CSV row: `complaint_id, category, priority, reason, flag`. 
  Verification: (1) `category` ∈ allowed list, (2) `priority` matches severity rule, (3) `reason` quotes words from `description`, (4) `flag` is `NEEDS_REVIEW` iff `category=Other` or ambiguous. Reviewer can trace every output to enforcement without guessing.

context: >
  Allowed: `description` and `complaint_id` from `data/city-test-files/test_[city].csv` (15 rows/city). 
  Explicit exclusions: ward/location/city columns, external knowledge, LLM priors, assumptions about intent, invented synonyms, cross-row aggregation. Only lowercased keyword matching on `description`.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no Water Damage."
  - "Priority is Urgent iff description (case-insensitive) contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Else Standard. (Low not inferred)."
  - "Every output row must include a reason field that cites the specific matched keyword/phrase and quotes the description, e.g., Matched 'pothole' in description: \"...\""
  - "If no category keyword matches or description is empty/whitespace, output category Other and flag NEEDS_REVIEW. Never guess. Flag BAD_ROW only on exception with reason Error: <msg>."
