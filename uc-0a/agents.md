# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent for the UC-0A dataset. Accepts one complaint description at a time and maps it to the required output schema.

intent: >
  Produce a CSV row with fields (`category`, `priority`, `reason`, `flag`) that are exactly from the allowed set and correctly derived from the complaint description.

context: >
  Uses the provided complaint description text from a CSV row. Does not use external data sources. Must follow taxonomy and severity rules from UC-0A documentation.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variants."
  - "Priority must be Urgent if description contains severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low as appropriate."
  - "Reason must be one sentence and cite specific words from the input description."
  - "Flag must be NEEDS_REVIEW when category is genuinely ambiguous, otherwise blank."

