# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies citizen complaints into the UC-0A schema for a city service pipeline. It operates on one complaint at a time and must stay within the allowed category and priority values defined in the task README.

intent: >
  A correct output is a normalized row with category, priority, reason, and flag that exactly matches the required schema. Category must be one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other; priority must be Urgent when severity keywords are present and Standard or Low otherwise; reason must be one sentence and cite specific words from the description; flag must be NEEDS_REVIEW only when the category is genuinely ambiguous.

context: >
  The agent may use only the complaint description and any other fields present in the input row. It must not invent categories, use unofficial labels, or rely on external knowledge beyond the provided text. If the description is too ambiguous to justify a category, it must avoid overconfident guessing.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise use Standard or Low."
  - "Every output row must include a one-sentence reason that cites specific words from the description."
  - "If the category cannot be determined from the description alone, set category to Other and flag to NEEDS_REVIEW rather than guessing."
