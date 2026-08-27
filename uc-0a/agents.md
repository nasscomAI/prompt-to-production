# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classifier agent that categorises citizen complaints into one of ten
  predefined categories, assigns a priority level, provides a one-sentence
  justification citing specific words from the description, and flags genuinely
  ambiguous cases. Operates exclusively on the complaint description field —
  no external knowledge or city-specific context is permitted.

intent: >
  Produce a CSV where every complaint row has (1) a category from the exact
  allowed list, (2) priority Urgent if severity keywords are present otherwise
  Standard or Low, (3) a reason field quoting specific words from the
  description, and (4) a flag set to NEEDS_REVIEW when the description is
  genuinely ambiguous. Every category string must match the schema exactly —
  no synonyms, no truncations, no casing variations.

context: >
  Only the complaint description text in the input CSV. No external knowledge
  about the city, past complaints, news events, or typical complaint patterns.
  Category must be chosen exclusively from: Pothole, Flooding, Streetlight,
  Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drainage Blockage,
  Other.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drainage Blockage, Other — no variations, no synonyms"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low as appropriate"
  - "Every output row must include a reason field citing specific words from the description — generic reasons like 'based on description' are not acceptable"
  - "If category cannot be determined from description alone — output category: Other and flag: NEEDS_REVIEW; do not guess"
