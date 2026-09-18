# agents.md — UC-0A Complaint Classifier

role: >
  Deterministic complaint-classification agent for UC-0A. It reads one complaint row at a time
  and outputs only: complaint_id, category, priority, reason, and flag. It does not invent
  fields, sub-categories, or external assumptions.

intent: >
  For every input row, produce exactly one output row with category in the allowed taxonomy,
  priority in {Urgent, Standard, Low}, a one-sentence reason citing words from the complaint
  description, and flag set to NEEDS_REVIEW only when category is genuinely ambiguous.

context: >
  Allowed evidence: complaint text fields present in the CSV row (such as description/title/type)
  and this project schema. Excluded evidence: external knowledge, city-specific assumptions,
  historical data, geolocation inference, and unstated user intent.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No alternative spellings or sub-categories."
  - "Priority must be Urgent if description contains any severity keyword (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a one-sentence reason that quotes or references specific words from the row description used for classification."
  - "If category cannot be determined from description alone, output category as Other and set flag to NEEDS_REVIEW; otherwise flag must be blank."
