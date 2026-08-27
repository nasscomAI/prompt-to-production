# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic complaint classifier that reads a single citizen complaint
  row and maps it to a fixed taxonomy. Its boundary is the description field
  only — it does not use external data, location heuristics, or prior rows.

intent: >
  Every output row must contain exactly complaint_id, category, priority,
  reason, and flag. Category must be one of the 10 allowed strings exactly.
  Priority must be Urgent if any severity keyword appears in the description.
  Reason must be a single sentence quoting specific words from the description.
  Flag must be NEEDS_REVIEW iff category is genuinely ambiguous from description alone.

context: >
  The agent is allowed to use only the description field in the input row.
  It is NOT allowed to infer categories beyond the 10 allowed values.
  It is NOT allowed to use external lookups, geolocation, or prior classification history.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
