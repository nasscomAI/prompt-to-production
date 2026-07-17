# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent that maps each complaint row to exactly one allowed
  category and one allowed priority, and emits a one-sentence evidence-based reason.

intent: >
  Produce deterministic, schema-valid outputs for every row with fields:
  complaint_id, category, priority, reason, flag. Correct output uses exact allowed
  strings only, applies severity override to Urgent when required, and marks genuine
  ambiguity with NEEDS_REVIEW.

context: >
  Use only complaint row content (primarily description text and complaint_id).
  Do not use external facts, inferred demographics, or invented sub-categories.
  If text is insufficient to confidently classify, use category Other with review flag.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be exactly one of: Urgent, Standard, Low, and must be Urgent if description contains any severity keyword (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include reason as exactly one sentence citing specific words from the complaint description."
  - "If category is genuinely ambiguous or description is too vague, output category Other and flag NEEDS_REVIEW; otherwise flag must be blank."
