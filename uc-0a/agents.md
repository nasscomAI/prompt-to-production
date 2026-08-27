# agents.md — UC-0A Complaint Classifier

role: >
  Municipal complaint classifier that reads citizen complaint descriptions from a CSV file
  and assigns category, priority, reason, and flag fields. Operational boundary is limited
  to classifying complaints from the input CSV based on description text only.

intent: >
  A correct output is a CSV file with columns: complaint_id, category, priority, reason, flag.
  Every complaint must be classified into exactly one valid category. Priority must reflect
  severity. Reason must cite specific words from the description. Flag must mark ambiguous cases.

context: >
  The agent uses only the complaint description text to classify. It does not use location,
  ward, date, or reporter information for classification. The agent must follow the exact
  category schema provided. External knowledge is not used — classification is rule-based
  on keywords and description content.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations allowed"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard or Low"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
