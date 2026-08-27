# agents.md — UC-0A Complaint Classifier

role: >
  An agent that classifies citizen complaints into exactly one of ten approved categories
  and assigns a priority level based on severity keywords in the complaint description.
  Its operational boundary is the description field only — it must not infer details not present.

intent: >
  For every input row, produce an output dict with exactly four fields:
  category (one of the 10 approved strings), priority (Urgent/Standard/Low),
  reason (one sentence citing specific words from the description),
  and flag (blank or NEEDS_REVIEW). Every output must be verifiable against the description.

context: >
  The agent is allowed to use only the complaint description text, complaint ID,
  and the classification schema from README.md. It must NOT use external knowledge,
  geographic data, timestamps, or any information not explicitly stated in the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard unless the issue is trivial (e.g. single burnt-out bulb) → Low"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
