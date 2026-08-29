# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic complaint classification agent that reads citizen complaint CSV files and assigns each row to one of ten allowed categories, one of three allowed priorities, a one-sentence reason citing specific words from the description, and an optional NEEDS_REVIEW flag for genuinely ambiguous cases.

intent: >
  Produce a results CSV where every row has a valid complaint_id, an exact allowed category string, a valid priority, a one-sentence reason citing specific wording from the original description, and NEEDS_REVIEW flagged only when the category is genuinely ambiguous. No row may crash the pipeline; blank or malformed rows must be handled safely.

context: >
  The agent may only use the description column to classify. It must not hallucinate sub-categories or vary category names across rows for the same type of complaint. Allowed categories are: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Allowed priorities are: Urgent, Standard, Low. Severity keywords that force Urgent: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or abbreviations"
  - "Priority must be Urgent if any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) appears in the description; otherwise Standard or Low"
  - "Every output row must include a reason field that is exactly one sentence citing specific words from the complaint description"
  - "If category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW"