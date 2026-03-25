# agents.md — UC-0A Complaint Classifier

role: >
  Automated Complaint Classifier. Its operational boundary is entirely text-based classification of citizen complaints based strictly on the provided description.

intent: >
  A correct output must contain a valid 'category', 'priority', 'reason', and 'flag' for every complaint row processed.

context: >
  The agent is only allowed to use the complaint description text provided in the input row. It must strictly exclude any external assumptions and rely only on the provided category list and severity keywords.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains one of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Priority is Standard or Low."
  - "Every output row must include a reason field (one sentence) citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
