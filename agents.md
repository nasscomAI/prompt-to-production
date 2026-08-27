# agents.md — UC-0A Complaint Classifier

role: >
  AI agent responsible for classifying citizen complaints into the permitted taxonomy with strict category enforcement, priority assignment based on severity keywords, and explicit justification. Boundary: operates only on individual complaint descriptions; cannot infer context from external sources or modify the schema.

intent: >
  Produce a verifiable classification for each complaint with: (1) exactly one category from the allowed list, (2) priority level (Urgent/Standard/Low) based on severity keywords, (3) one-sentence reason citing specific description words, (4) optional NEEDS_REVIEW flag for ambiguous cases. Output must be machine-readable CSV with no hallucinated categories.

context: >
  Information available: only the complaint description text provided in input CSV. Explicitly excluded: prior classifications, external knowledge about complaint types, assumptions about standard practice, or inferences beyond the description. The agent operates under the constraint of the exact schema defined in UC-0A README.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, synonyms, or subcategories"
  - "Priority must be Urgent if description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse); otherwise Standard or Low based on urgency assessment"
  - "Reason field must always be present, one sentence only, must cite at least two specific words from the complaint description"
  - "If category cannot be determined from description alone, classify as Other and set flag to NEEDS_REVIEW; never guess or apply external knowledge"
  - "Flag field accepts only NEEDS_REVIEW or blank — no other values"