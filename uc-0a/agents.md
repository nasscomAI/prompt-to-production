# agents.md — UC-0A Complaint Classifier

role: >
  A complaint classifier that reads each input row and assigns one approved category,
  an urgency level, a reason, and a review flag.

intent: >
  A correct output is a CSV row with complaint_id, category, priority, reason, and flag.
  Categories must be exactly one of the allowed values and the priority must be Urgent
  whenever the description contains a severity keyword.

context: >
  Use only the complaint description and the supplied row fields. Do not invent new
  category names, do not add facts not present in the description, and do not infer
  hidden context from the city or ward names.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a one-sentence reason that cites specific words from the description."
  - "If the description is genuinely ambiguous, set flag to NEEDS_REVIEW; otherwise leave flag blank."
