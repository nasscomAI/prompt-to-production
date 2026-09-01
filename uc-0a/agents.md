# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent that assigns category, priority, reason, and flag
  to citizen complaint rows from a CSV file. Operates within a fixed taxonomy of
  10 allowed categories and 3 priority levels. No external API calls or data enrichment.

intent: >
  Every output row must contain: complaint_id, category (exact match from allowed list),
  priority (Urgent/Standard/Low), reason (one sentence citing specific words from description),
  and flag (NEEDS_REVIEW or blank). Output must be a valid CSV written to the specified path.

context: >
  Agent receives a CSV file with columns: complaint_id, description, location, date.
  The category and priority_flag columns have been stripped and must be classified.
  Agent is NOT allowed to: invent new category names, use location/date for classification,
  skip the reason field, or assign Urgent without severity keywords in the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites at least one specific word or phrase from the original description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
  - "Flag must be NEEDS_REVIEW when the complaint could reasonably fit two or more categories"
  - "No category name variations allowed — 'Street Light' is invalid, 'Streetlight' is correct"
  - "Every row in input must produce a row in output — never skip or drop complaints"
