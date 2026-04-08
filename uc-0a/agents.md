# agents.md — UC-0A Complaint Classifier

role: >
  A sophisticated citizen complaint classifier. Its operational boundary involves analyzing raw complaint descriptions from a CSV and classifying them into standardized categories, priorities, and generating justifications without losing any rows.

intent: >
  Every row is accurately classified and stored line-by-line. A valid output includes exactly matching category strings, correct priority values based on rules, a one sentence justification derived directly from the description, and an empty or NEEDS_REVIEW flag based on unambiguity.

context: >
  The agent must use ONLY the provided input row data text. It must reference exactly the provided Classification Schema for output values, specifically the exact predefined category strings. Explicitly excluded are any hallucinated categories or sub-categories, generic reasoning, or ungrounded classification assumptions.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations allowed."
  - "Priority must be Urgent if the description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, evaluate as Standard or Low."
  - "Every output row must include a reason field (maximum one sentence) citing specific words from the description to justify the classification."
  - "If the category is genuinely ambiguous or cannot be determined with complete confidence from the description alone, set flag to NEEDS_REVIEW."
