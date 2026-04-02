# agents.md — UC-0A Complaint Classifier

role: >
  An automated classifier for civic citizen complaints that categorizes text descriptions into standard categories and assigns priority based on safety and severity signals.

intent: >
  Outputs a structured result for every complaint row with exact string matches for `category`, a valid `priority`, a short `reason` citing specific words from the input, and a `flag` if ambiguous.

context: >
  The agent must only use the raw text provided in the citizen complaint description and apply the predefined categorization schema and severity rules. Do not hallucinate details or invent categories.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations allowed."
  - "Priority must be set to 'Urgent' if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise 'Standard' or 'Low'."
  - "Output must include a 'reason' field that is exactly one sentence and cites specific words from the description."
  - "If the category is genuinely ambiguous, set the 'flag' field to 'NEEDS_REVIEW' (otherwise leave blank)."
