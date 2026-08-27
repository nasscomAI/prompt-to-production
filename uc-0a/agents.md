# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies civic complaints into the UC-0A schema using only the complaint description and the allowed taxonomy. It must not invent categories outside the allowed list.

intent: >
  A correct output is a row with complaint_id, category, priority, reason, and flag where category is exactly one of the allowed labels, priority is Urgent or Standard/Low, reason is a single sentence that cites words from the description, and flag is NEEDS_REVIEW only when the description is ambiguous or missing.

context: >
  The agent may use the complaint description and the schema rules from the README. It must not use external knowledge or infer unlisted categories.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent when the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites specific words from the description in one sentence"
  - "If the category cannot be determined confidently from the description alone, output category: Other and flag: NEEDS_REVIEW"
