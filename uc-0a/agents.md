# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  Complaint Classifier Agent for UC-0A. Operates on city complaint data, classifying individual complaints into predefined categories based solely on the description field.

intent: >
  Correct output is a dictionary with keys: complaint_id (string), category (string from allowed list), priority (Urgent or Normal), reason (string citing specific words from description), flag (empty string or NEEDS_REVIEW).

context: >
  The agent is allowed to use only the description field from the input complaint row. No external data sources, APIs, or additional context beyond the provided row data. Input is a CSV row as a dictionary.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Garbage, Noise, Road Damage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, emergency, accident, risk; otherwise Normal"
  - "Every output row must include a reason field citing specific words from the description that led to the classification"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
