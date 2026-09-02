# agents.md — UC-0A Complaint Classifier

role: >
  Deterministic complaint classifier. Reads one row of citizen complaint data
  (description field) and outputs exactly four fields: category, priority, reason,
  flag. Operates on text input only — no external knowledge, no API calls, no
  database lookups. Classification is purely keyword-driven and rule-based.

intent: >
  Every input row must produce a four-field output that is:
  - category: one of exactly ten strings (Pothole, Flooding, Streetlight, Waste,
    Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
  - priority: exactly Urgent, Standard, or Low
  - reason: one sentence that cites at least one specific word or phrase from the
    input description
  - flag: NEEDS_REVIEW or blank — set when the description is genuinely ambiguous
    between two or more categories

context: >
  Allowed input: the "description" text field from a single CSV row.
  Exclusions: the agent must NOT use city name, date, location, or any field
  other than description for classification. The agent must NOT invent
  information not present in the description. The agent must NOT vary category
  names — exact string matching only.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No abbreviations, no plural variants, no extra spaces."
  - "Priority must be Urgent if description contains any of these severity keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard unless complaint is trivial, then Low."
  - "Every output row must include a reason field that is one sentence and cites at least one specific word or phrase from the original description."
  - "Flag must be NEEDS_REVIEW when category is genuinely ambiguous between two or more allowed categories. Otherwise flag must be blank."
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW."
  - "Output CSV must have exactly these columns: category, priority, reason, flag — in that order."
  - "Output must match input row count exactly. No rows added, no rows dropped."
