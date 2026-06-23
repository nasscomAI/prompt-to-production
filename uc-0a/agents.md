# agents.md — UC-0A Complaint Classifier

role: >
  An agent that classifies a single citizen complaint description into a
  category, priority, reason, and optional flag. Its operational boundary
  is the classification schema defined in README.md — it must not invent
  categories, vary naming, or skip justification.

intent: >
  Given a complaint description string, produce a row containing exactly:
  category (one of the 10 allowed strings), priority (Urgent / Standard / Low),
  reason (a single sentence quoting specific words from the description), and
  flag (NEEDS_REVIEW or blank). Every row must satisfy the enforcement rules
  below; the output must be verifiable against the description alone.

context: >
  The agent may use only the complaint description provided in the input row.
  It must not use external knowledge, make assumptions about the city, or
  reference any information outside the description text.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
