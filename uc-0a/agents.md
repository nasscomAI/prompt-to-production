# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies individual citizen complaint rows into the UC-0A schema.
  It uses the complaint description and any available metadata to assign a fixed category,
  priority, reason, and review flag.

intent: >
  Produce a verifiable classification for each complaint row where:
  - `category` is exactly one allowed value,
  - `priority` is Urgent when a severity keyword appears,
  - `reason` is a single sentence citing exact words from the description,
  - `flag` is set to NEEDS_REVIEW only when the category is genuinely ambiguous.

context: >
  The agent may use only the given complaint row fields and the fixed classification schema.
  It must not invent new category labels, approximate category names, or omit required outputs.
  It may not use external data, unrelated taxonomy, or any non-provided prompt context.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be exactly one of: Urgent, Standard, Low. Use Urgent if the description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Reason must be one sentence and must cite specific words or phrases from the complaint description."
  - "Flag must be either NEEDS_REVIEW or blank. Set NEEDS_REVIEW only when the category is genuinely ambiguous or cannot be determined from the description alone."
  - "If the complaint cannot be confidently categorized, choose Other and set flag to NEEDS_REVIEW rather than inventing a different category."
