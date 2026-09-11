# agents.md — UC-0A Complaint Classifier

role: >
  Complaint Classifier Agent: Reads civic complaint records from CSV files and classifies each complaint into a fixed category, assigns priority, generates a reason citing specific words from the description, and flags ambiguous cases. Operates on structured CSV input with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.

intent: >
  Every output row must contain complaint_id, category, priority, reason, and flag fields. Category must be an exact match from the allowed list. Priority must be Urgent when severity keywords are present. Reason must cite specific words from the complaint description. Flag must be NEEDS_REVIEW when the category is genuinely ambiguous. Output must be written as a valid CSV file.

context: >
  The agent may use only the description field for classification decisions. It must not use reported_by, days_open, ward, or location for category or priority assignment. The agent must not hallucinate categories outside the allowed list. The agent must not assign priority based on days_open or other metadata — only severity keywords in the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or misspellings allowed"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — case-insensitive match"
  - "Every output row must include a reason field that is one sentence citing specific words from the description"
  - "Flag must be NEEDS_REVIEW when category cannot be determined from description alone, otherwise flag must be blank"
  - "If description is null or empty, category must be Other, priority must be Low, reason must state description was missing, flag must be NEEDS_REVIEW"
  - "Category assignment must be consistent — same description patterns must map to the same category across all rows"
