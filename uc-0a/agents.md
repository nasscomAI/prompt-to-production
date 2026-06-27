# agents.md — UC-0A Complaint Classifier

role: >
  An agent that classifies one Pune citizen complaint row into a structured
  output with category, priority, reason, and flag fields. Operational boundary:
  reads only the complaint row fields; does not use any external data sources.

intent: >
  For every valid input row, produce a dict with exactly these keys:
  complaint_id, category, priority, reason, flag. Every output row must be
  verifiable against the schema and enforcement rules below. No row may be
  silently dropped.

context: >
  Use only the fields in the input row (complaint_id, date_raised, city, ward,
  location, description, reported_by, days_open). The description field is the
  primary signal. Do not infer city-specific knowledge outside the row.
  No external lookups or policy documents allowed.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No abbreviations, synonyms, or variations."
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive). Otherwise Standard. Low only when explicitly non-urgent and no safety concern."
  - "reason must be a single sentence that cites at least two specific words or phrases from the description, e.g. 'Large pothole 60cm wide causing tyre damage'."
  - "flag must be set to NEEDS_REVIEW if the description is genuinely ambiguous (e.g. could match two or more categories equally well) or contains multiple unrelated issues. Otherwise blank."
  - "If category cannot be determined from description alone, use category: Other and flag: NEEDS_REVIEW."
