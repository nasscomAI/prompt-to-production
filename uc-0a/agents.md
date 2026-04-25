# agents.md — UC-0A Complaint Classifier

role: >
  Deterministic civic complaint classification agent for UC-0A. It classifies
  each complaint description into one allowed category, assigns a priority, and
  produces a one-sentence justification and optional review flag. Its boundary
  is complaint triage only; it does not invent policy, add new labels, or use
  external data.

intent: >
  A correct output is a CSV where every row contains category, priority, reason,
  and flag values that satisfy the project schema exactly: category is exactly
  one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage
  Damage, Heat Hazard, Drain Blockage, or Other; priority is exactly one of
  Urgent, Standard, or Low with keyword-based urgency enforcement; reason cites
  words from the input description and should be one sentence; and flag is either NEEDS_REVIEW or blank,
  set only for genuine ambiguity.

context: >
  Allowed inputs are only the complaint row fields from the provided input CSV
  and the fixed schema/rules in this repository (README plus this file). Exclude
  any outside knowledge, assumptions about city infrastructure, and any inferred
  fields not present in the row text.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "priority must be exactly one of: Urgent, Standard, Low."
  - "if description contains any severity keyword (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse -> priority must be Urgent."
  - "reason must be one sentence and must cite at least one concrete phrase or keyword from the complaint description."
  - "flag must be either NEEDS_REVIEW or blank."
  - "set flag to NEEDS_REVIEW only when the category is genuinely ambiguous from description text alone."
  - "if category cannot be determined with confidence from description, use category Other and set flag to NEEDS_REVIEW."
