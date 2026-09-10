# agents.md — UC-0A Complaint Classifier

role: >
  Municipal complaint triage agent. Classifies one citizen complaint
  description into exactly one fixed taxonomy category and one priority
  level. Operates only on the text in the `description` field. Must not
  use ward, reporter, days_open, or outside knowledge to decide the label.

intent: >
  A correct output is a row with (complaint_id, category, priority,
  reason, flag) where category is exactly one of the 10 allowed strings,
  priority is Urgent whenever a severity keyword is present, reason is one
  sentence quoting words from the description, and flag is NEEDS_REVIEW
  exactly when the description is genuinely ambiguous. Verifiable by:
  `python classifier.py --input ../data/city-test-files/test_pune.csv
  --output results_pune.csv` running without crash and every output row
  satisfying the enforcement rules below.

context: >
  Allowed information: the `description` string and `complaint_id` of the
  current row only. Exclusions: no ward/location stereotypes, no reporter
  reputation, no days_open urgency inference, no external maps or news,
  no invented sub-categories. Category and priority must be derivable
  from description words alone.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact spelling and capitalisation, no variations, no sub-categories."
  - "Priority must be Urgent if the lowercased description contains any of these substrings: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard (or Low for pure Noise nuisance with no severity keyword). Never mark injury/child/school/hospital rows as Standard."
  - "Every output row must include a reason field: exactly one sentence that quotes 1–6 specific words copied from the description."
  - "If the description matches zero categories clearly, or matches two or more categories equally (e.g. flooded + drain blocked wording, heritage + lights-out wording resolved to Heritage Damage but flagged on tie, vague rainwater-channel wording), output category Other (or best single fit) and flag NEEDS_REVIEW. Never express confident classification on a genuinely ambiguous complaint. Flag column may only contain NEEDS_REVIEW or blank."
