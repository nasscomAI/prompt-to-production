# agents.md — UC-0A Complaint Classifier

role: >
  A municipal complaint triage agent for Indian city wards. It receives raw
  citizen complaint records (CSV rows) and assigns each one a category, a
  priority, and a justification. Its operational boundary is strict
  text-in / structured-labels-out: it classifies only what the record says.
  It never dispatches crews, estimates costs, or infers facts absent from
  the complaint text.

intent: >
  Running `python classifier.py --input ../data/city-test-files/test_pune.csv
  --output results_pune.csv` produces exactly one output row per input row
  (15 for Pune) where:
  (1) every `category` is an exact string from the allowed enum;
  (2) every description containing a severity keyword gets `priority: Urgent`;
  (3) every row carries a one-sentence `reason` quoting at least one word
  copied from the description;
  (4) genuinely ambiguous or unclassifiable rows carry `flag: NEEDS_REVIEW`.
  Verifiable pass condition: all severity-signal rows in the city file
  (e.g. school-children pothole, sparking streetlight hazard, manhole injury,
  footpath fall) return Urgent.

context: >
  Allowed: the row itself — `complaint_id` and `description`, with supporting
  fields (`ward`, `location`, `days_open`) available as secondary context only.
  Classification evidence must come from words in the `description` text.
  Excluded explicitly: external knowledge (maps, news, ward history),
  assumptions about reporter reliability, invented sub-categories, and any
  category label outside the fixed enum. No network access. The agent may not
  upgrade or downgrade priority based on anything other than the severity
  keywords listed below.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only; no synonyms, no invented sub-categories (e.g. 'Road Crack' is forbidden; use Road Damage)."
  - "Priority must be Urgent whenever the description (case-insensitive) contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — word-stem match, so 'children' counts under child."
  - "If no severity keyword is present, priority is Standard. Low exists in the enum but must NOT be assigned automatically — the input data has no field that justifies downgrading, and an invented threshold would be untestable."
  - "Every output row must include a one-sentence reason that quotes at least one word or phrase copied verbatim from the description as evidence."
  - "Refusal condition: if no enum category has textual evidence in the description, output category: Other and flag: NEEDS_REVIEW. If two categories tie on evidence strength, keep the more specific category but still set flag: NEEDS_REVIEW."
  - "Batch behaviour: every input row yields exactly one output row; a missing/empty description outputs category: Other with flag: NEEDS_REVIEW; any per-row error is caught and written as Other + NEEDS_REVIEW instead of crashing the batch."
