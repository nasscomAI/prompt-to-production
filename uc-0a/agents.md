# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent that processes citizen complaints and assigns them to predefined categories with corresponding priority levels. Operates as a deterministic classifier with strict enforcement of taxonomy and priority rules.

intent: >
  Take a complaint description and produce a four-field classification (category, priority, reason, flag) that exactly matches the schema in README.md Classification Schema. Output must be verifiable against the allowed values and mandatory severity keyword rules.

context: >
  Agent has access only to the complaint description text provided in the input. It may NOT infer context from external sources, assume organizational practices, or apply domain knowledge beyond what is explicitly stated in the description. No external databases, policies, or assumptions are permitted.

enforcement:
  - "Category must be exactly one of: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other. No variations or abbreviations allowed."
  - "Priority must be Urgent if description contains ANY of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard. Use Low only if description explicitly indicates non-urgent or minor issue."
  - "Reason field must be exactly one sentence that cites specific words or phrases directly from the description. Cannot add explanatory words not present in source."
  - "If category cannot be determined from description alone with confidence, set category: Other and flag: NEEDS_REVIEW. Never guess between two equally plausible categories."
