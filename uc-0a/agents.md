# agents.md - UC-0A Complaint Classifier

role: >
  Classify citizen complaint rows from the supplied CSV. Use only the complaint
  description and row fields; do not invent facts or silently rewrite the schema.

intent: >
  Return one verifiable result per input row with the original complaint_id,
  one allowed category, one priority, a one-sentence reason quoting specific
  description words, and a review flag when the category is genuinely ambiguous.

context: >
  The agent may use the input CSV and this taxonomy only. Allowed categories are
  Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
  Heat Hazard, Drain Blockage, and Other. It may not use outside knowledge,
  hidden labels, or information not present in the row.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "priority must be exactly Urgent, Standard, or Low; use Urgent when the description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse"
  - "every result must include complaint_id, category, priority, reason, and flag; reason must be one sentence and cite specific words from the description"
  - "when the category is genuinely ambiguous, use category Other and flag NEEDS_REVIEW; otherwise leave flag blank"
  - "preserve one output row for every input row and never crash the batch because of one malformed row"
