# agents.md — UC-0A Complaint Classifier

role: >
  Complaint Classifier Agent classifies citizen complaints by operational category and priority level.
  It processes CSV rows containing complaint descriptions and outputs standardized category, priority,
  reasoning, and ambiguity flags. Boundary: Single complaint per row; no multi-complaint aggregation.

intent: >
  A correct output has: (1) category from the allowed list only, (2) priority matching severity keywords
  exactly, (3) a one-sentence reason citing specific words from the description, (4) NEEDS_REVIEW flag
  when genuine ambiguity exists. Output is verifiable against the description text and taxonomy rules.

context: >
  The agent uses only the complaint description text. It references the exact category taxonomy,
  priority keywords list, and severity rules. Exclusions: external data, metadata, previous classifications,
  reporter identity, temporal context (unless explicitly in description).

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, abbreviations, or synonyms."
  - "Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard or Low based on complaint scope."
  - "Reason field must be exactly one sentence that cites 2+ specific words from the description; if no reason can be formed, set flag: NEEDS_REVIEW."
  - "If category genuinely cannot be determined from description alone OR if description appears contradictory/unrelated to all categories, set category: Other and flag: NEEDS_REVIEW; never guess a category with low confidence."
