# agents.md — UC-0A Complaint Classifier

role: >
  [FILL IN: Who is this agent? What is its operational boundary?]

intent: >
  [FILL IN: Classify each complaint into exactly one allowed category and one priority, provide a one-sentence reason citing specific words from the complaint description, and set the review flag when the complaint is genuinely ambiguous.]

context: >
  Use only the complaint row and the UC-0A classification rules defined in README.md.
  The allowed categories are: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
  The allowed priorities are: Urgent, Standard, Low.
  The flag must be either NEEDS_REVIEW or blank.
  Do not use external assumptions or invent information not present in the complaint.

enforcement:
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
  - Priority must be exactly one of: Urgent, Standard, Low.
  - If the complaint contains any severity keyword such as injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse, priority must be Urgent.
  - Every output must contain a one-sentence reason that cites specific words from the complaint description.
  - If the category cannot be determined confidently from the description alone, use Other and set flag to NEEDS_REVIEW.
  - Never create category names outside the allowed taxonomy.
  - Never invent sub-categories or unsupported facts.
  - Ambiguous complaints must not receive unjustified confident classifications.
