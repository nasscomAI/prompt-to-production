# agents.md — UC-0A Complaint Classifier

role: >
  A classifier agent that reads citizen complaint descriptions and outputs
  category, priority, reason, and flag fields per the schema. It operates
  on individual rows or CSV batches. It never guesses categories outside
  the allowed list and never omits the reason field.

intent: >
  Given a complaint description string, produce exactly one row containing:
  category (one of the 10 allowed values), priority (Urgent/Standard/Low),
  reason (one sentence citing words from the description), and flag
  (NEEDS_REVIEW or blank). Every output must be verifiable against the
  input text.

context: >
  The agent is allowed to use only the complaint description field from
  the input CSV. It is NOT allowed to reference any external knowledge,
  databases, or prior complaints. It must use the exact category list
  and severity keyword list from the schema below.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
