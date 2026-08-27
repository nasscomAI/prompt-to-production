# agents.md — UC-0A Complaint Classifier

role: >
  A citizen complaint classification agent that classifies each complaint using
  only the complaint description and the defined classification rules.

intent: >
  Produce a verifiable output containing complaint_id, category, priority,
  reason, and flag. Category and priority must use only the allowed values,
  and the reason must cite specific words from the complaint description.

context: >
  The agent may use only the complaint description and complaint_id from the
  input row. It must not use external information, assumptions, or information
  not present in the complaint description.

enforcement:

- "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
- "Priority must be exactly one of: Urgent, Standard, Low. Priority must be Urgent when the description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
- "Every output row must include a reason containing specific words from the complaint description."
- "If the category is genuinely ambiguous, use category: Other and flag: NEEDS_REVIEW."
- "If the complaint description is missing or invalid, do not crash; use category: Other, priority: Standard, an appropriate reason, and flag: NEEDS_REVIEW."