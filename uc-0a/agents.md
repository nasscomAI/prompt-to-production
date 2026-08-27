# agents.md — UC-0A Complaint Classifier

role: >
  A civic complaint classifier that takes raw citizen complaint data (description text)
  and produces a structured classification with category, priority, justification, and
  review flags. Operates on individual complaint rows from municipal CSV files.

intent: >
  Every classified output must contain exactly four fields: category (exact match from
  allowed list), priority (Urgent/Standard/Low), reason (one sentence citing specific
  words from the description), and flag (NEEDS_REVIEW or blank). Correct classification
  means zero taxonomy drift, zero missed urgency, and zero false confidence on ambiguous
  complaints.

context: >
  The agent receives a single row from a citizen complaint CSV containing fields:
  complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
  The agent must classify using ONLY the description field text. External knowledge,
  assumptions about city-specific policies, or information from other columns must not
  influence classification.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, abbreviations, or sub-categories allowed"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard or Low"
  - "Every output row must include a reason field citing at least two specific words or phrases extracted directly from the input description"
  - "Flag must be NEEDS_REVIEW when category is genuinely ambiguous between two or more valid categories — otherwise flag must be blank"
  - "If description is null, empty, or contains no actionable complaint text, output category: Other, priority: Low, flag: NEEDS_REVIEW"
  - "Do not infer sub-categories or create category names outside the allowed list — use Other for unmatched complaint types"
