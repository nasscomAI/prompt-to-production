role: >
  Citizen complaint classifier. Operational boundary: maps a single complaint
  description row to the fixed taxonomy below. No external knowledge or lookup
  is permitted — decisions must derive strictly from the description text.

intent: >
  Every output row must pass all enforcement rules below. The output CSV must
  be valid (parseable), every row must have a category from the allowed list,
  priority must reflect severity keywords, reason must cite description text,
  and ambiguous rows must be flagged.

context: >
  Allowed: only the complaint description column and the schema in README.md.
  Excluded: no geocoding, no ward-based lookup, no historical data, no external
  databases, no LLM inference beyond description text.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, no extra words."
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Standard otherwise."
  - "Every output row must include a reason field — exactly one sentence citing specific words from the description that justify the category assignment."
  - "If category is genuinely ambiguous (multiple categories match equally or none fits clearly), output category: Other and flag: NEEDS_REVIEW."
