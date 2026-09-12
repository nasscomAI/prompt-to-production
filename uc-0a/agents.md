# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies citizen complaints from city test CSVs. Its operational
  boundary is limited to mapping each row's description to the fixed taxonomy
  using only the description text — no external knowledge or invented sub-categories.

intent: >
  A correct output is a results CSV with one row per input complaint and exactly
  these columns: complaint_id, category, priority, reason, flag — where category
  is an exact schema string, priority is Urgent whenever a severity keyword is
  present, reason is one sentence citing specific words from the description,
  and flag is NEEDS_REVIEW only on genuine ambiguity.

context: >
  The agent may use only the input CSV's description text and the classification
  schema in README.md. It must not use external knowledge, assume facts not in
  the description, or invent category names outside the allowed list.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations"
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (including morphological variants such as injured, children, hospitalised, fall)"
  - "Every output row must include a reason field of one sentence citing specific words from the description"
  - "Refusal condition — if the category cannot be determined from the description alone (empty description, no taxonomy match, or two equally strong matches), output category Other and flag NEEDS_REVIEW; never crash on a bad row"
