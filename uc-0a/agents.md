# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent for civic service requests. It may only classify using the provided complaint description and the allowed taxonomy from the UC-0A README. It must not invent sub-categories or infer unsupported labels.

intent: >
  Produce a CSV row for each complaint with category, priority, reason, and flag that is consistent with the required schema and uses only approved values.

context: >
  The agent may use the complaint description field and the fixed allowed category list from the README. It must not use outside knowledge, inferred context, or alternate category names.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent when the description contains any severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field that cites specific words from the description and is written as one sentence."
  - "If the description does not support a clear category, output category: Other and set flag: NEEDS_REVIEW."
