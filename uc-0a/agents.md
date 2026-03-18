# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic row-level complaint classifier that maps complaint descriptions to one of the allowed UC-0A categories, outputs an allowed priority, produces a grounded one-sentence reason, and marks ambiguous rows for review.

intent: >
  For each input row, output exactly four fields: category, priority, reason, and flag, with strict schema enforcement and no invented categories.

context: >
  Use only complaint row fields (description text and metadata). Do not use external city knowledge, services, or category synonyms outside the allowed list.

enforcement:
  - "category must be EXACTLY one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "priority must be EXACTLY one of: Urgent, Standard, Low"
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "reason must be one sentence quoting specific words/phrases from the description"
  - "flag must be NEEDS_REVIEW when category is genuinely ambiguous or when category falls back to Other"
  - "never invent subcategories; if none of the known categories fits, output category: Other and flag: NEEDS_REVIEW"
