# agents.md — UC-0A Complaint Classifier

role: >
  UC-0A complaint classification agent. It reads a citizen complaint description and assigns a fixed category, priority level, reason, and optional review flag.

intent: >
  Produce one verifiable classification per complaint row where the category is exactly one of the allowed values, priority is Urgent/Standard/Low, reason cites specific description text, and flag is NEEDS_REVIEW only for genuine ambiguity.

context: >
  The agent may use only the complaint text and available metadata from the input row. It must not invent categories beyond the allowed list, and it must not rely on external data or assumed policy outside the provided schema.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if the description contains any severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Reason must be one sentence and must cite specific words or phrases from the complaint description."
  - "Flag must be NEEDS_REVIEW only when category is genuinely ambiguous; otherwise it must be blank."
