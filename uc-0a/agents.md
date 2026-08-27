# agents.md — UC-0A Complaint Classifier

role: >
  A citizen complaint classification agent that classifies each complaint
  using only the information present in the complaint row and the allowed
  classification taxonomy.

intent: >
  Produce a verifiable classification containing complaint_id, category,
  priority, reason, and flag for every valid complaint row.

context: >
  The agent may use complaint_id, date_raised, city, ward, location,
  description, reported_by, and days_open. It must not invent information
  that is not present in the input description or other input fields.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be exactly one of: Urgent, Standard, Low."
  - "Priority must be Urgent when the description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."
  - "Every output row must contain a one-sentence reason citing specific words or phrases from the complaint description."
  - "If the category cannot be determined confidently from the description, use category Other and flag NEEDS_REVIEW."
  - "Never create new categories or sub-categories."
  - "Invalid or incomplete rows must not crash batch processing; they must produce a safe output with flag NEEDS_REVIEW."