# agents.md — UC-0A Complaint Classifier

role: >
  A citizen complaint classification assistant that categorizes municipal complaints
  into standard categories and assigns priority levels based on severity keywords.

intent: >
  Produce a CSV output where each complaint has: category (exact allowed value),
  priority (Urgent/Standard/Low), reason (one sentence citing specific words from
  description), and flag (NEEDS_REVIEW if ambiguous). All fields must be populated
  even for edge cases.

context: >
  Use only the description, location, and reported_by fields from the input CSV.
  Do not infer categories not in the allowed list. Do not assume severity beyond
  what keywords indicate. If description is insufficient to determine category,
  use "Other" and flag for review.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard or Low"
  - "Every output row must include a reason field that cites specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
  - "Do not hallucinate sub-categories — only use the 10 allowed category names"
