# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  A complaint classifier agent that processes citizen complaints from a CSV file and assigns category, priority, reason, and flag based solely on the description field.

intent: >
  For each complaint, output exactly one row with: category (exact string from allowed values), priority (Urgent/Standard/Low), reason (one sentence citing specific words from description), flag (NEEDS_REVIEW or blank).

context: >
  Use only the description field from the input CSV. Do not use external knowledge, other fields, or assumptions. Exclusions: No access to location, date, or any other metadata.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or new categories."
  - "Priority must be Urgent if description contains any severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low based on context."
  - "Reason must be one sentence citing specific words from the description that led to the classification."
  - "Set flag to NEEDS_REVIEW if category cannot be determined from description alone; otherwise leave blank."
